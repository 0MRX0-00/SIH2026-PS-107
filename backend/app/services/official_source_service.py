"""
Official Source Evidence Lookup Service for e-BIS Sahayak.

Fetches relevant pages from official BIS and Government of India portals
to provide evidence context alongside Groq inference. No RAG, no embeddings,
no vector database — just lightweight HTTP retrieval with caching and validation.
"""
import asyncio
import hashlib
import logging
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union
from urllib.parse import urlparse, quote_plus

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Trusted official domains (whitelist)
# ---------------------------------------------------------------------------
TRUSTED_DOMAINS: List[str] = [
    "bis.gov.in",
    "www.bis.gov.in",
    "standards.bis.gov.in",
    "services.bis.gov.in",
    "manakonline.in",
    "www.manakonline.in",
    "egazette.gov.in",
    "www.egazette.gov.in",
    "consumeraffairs.nic.in",
    "www.consumeraffairs.nic.in",
    "dpiit.gov.in",
    "www.dpiit.gov.in",
    "commerce.gov.in",
    "www.commerce.gov.in",
    "india.gov.in",
    "www.india.gov.in",
    "legalaffairs.gov.in",
    "www.legalaffairs.gov.in",
]

# ---------------------------------------------------------------------------
# BIS portal search endpoints (known URL patterns)
# ---------------------------------------------------------------------------
BIS_SEARCH_URLS: Dict[str, str] = {
    "standard_search": "https://www.services.bis.gov.in:8071/php/BIS_2/bisconnect/dgms_search/Activation_search.php",
    "bismanak_catalog": "https://services.bis.gov.in/php/BIS_2/bismanak/index.php",
    "product_certification": "https://bis.gov.in/index.php/product-certification/",
    "laboratory_overview": "https://bis.gov.in/index.php/laboratory-overview/",
    "hallmarking": "https://bis.gov.in/index.php/hallmarking/",
    "crs_registration": "https://bis.gov.in/index.php/product-certification/scheme-ii-registration-scheme/",
    "qco_orders": "https://bis.gov.in/index.php/product-certification/quality-control-orders/",
    "manak_search": "https://www.services.bis.gov.in:8071/php/BIS_2/bisconnect/dgms_search/Standard_search.php",
    "bis_portal": "https://bis.gov.in",
    "manakonline_verify": "https://manakonline.in/MANAK/SearchLicence",
    "fmcs_scheme": "https://bis.gov.in/index.php/product-certification/scheme-x-fmcs/",
    "isi_scheme": "https://bis.gov.in/index.php/product-certification/products-under-compulsory-certification-scheme/",
}


class OfficialSourceEvidence:
    """Represents a piece of evidence retrieved from an official source."""

    def __init__(
        self,
        title: str,
        url: str,
        domain: str,
        retrieved_text: str,
        retrieval_date: str,
        source_type: str = "official_bis",
        is_verified_domain: bool = True,
    ):
        self.title = title
        self.url = url
        self.domain = domain
        self.retrieved_text = retrieved_text
        self.retrieval_date = retrieval_date
        self.source_type = source_type
        self.is_verified_domain = is_verified_domain

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "domain": self.domain,
            "retrieved_text": self.retrieved_text,
            "retrieval_date": self.retrieval_date,
            "source_type": self.source_type,
            "is_verified_domain": self.is_verified_domain,
        }


class TTLCache:
    """Simple in-memory cache with per-entry TTL (time-to-live)."""

    def __init__(self, default_ttl_seconds: int = 3600, max_entries: int = 500):
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._default_ttl = default_ttl_seconds
        self._max_entries = max_entries

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.time() > expiry:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if len(self._store) >= self._max_entries:
            self._evict_expired()
            if len(self._store) >= self._max_entries:
                oldest_key = min(self._store, key=lambda k: self._store[k][1])
                del self._store[oldest_key]
        expiry = time.time() + (ttl if ttl is not None else self._default_ttl)
        self._store[key] = (value, expiry)

    def _evict_expired(self) -> None:
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired_keys:
            del self._store[k]

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


class OfficialSourceService:
    """
    Lightweight service for fetching evidence from official BIS and GOI portals.

    Design principles:
    - No RAG, no embeddings, no vector database
    - HTTP fetch with timeout, retry, and domain validation
    - TTL cache to avoid redundant requests
    - Structured evidence extraction (title, URL, text snippet, retrieval date)
    - Never fabricates URLs or regulatory claims
    """

    def __init__(
        self,
        timeout_seconds: Optional[float] = None,
        cache_ttl_seconds: Optional[int] = None,
        max_cache_entries: Optional[int] = None,
        max_content_length: int = 8000,
        max_concurrent_requests: int = 3,
        verify_ssl: Union[bool, str] = True,
    ):
        from app.core.config import settings
        self.timeout = timeout_seconds if timeout_seconds is not None else getattr(settings, "OFFICIAL_SOURCE_TIMEOUT_SECONDS", 4.0)
        self.max_content_length = max_content_length
        self.max_concurrent_requests = max_concurrent_requests
        self.verify_ssl = verify_ssl
        self._cache = TTLCache(
            default_ttl_seconds=cache_ttl_seconds if cache_ttl_seconds is not None else getattr(settings, "OFFICIAL_SOURCE_CACHE_TTL_SECONDS", 3600),
            max_entries=max_cache_entries if max_cache_entries is not None else getattr(settings, "OFFICIAL_SOURCE_MAX_CACHE_ENTRIES", 500),
        )
        self._request_semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._request_timestamps: List[float] = []
        self._rate_limit_per_minute = getattr(settings, "OFFICIAL_SOURCE_RATE_LIMIT_PER_MINUTE", 30)

    # ------------------------------------------------------------------
    # Domain validation
    # ------------------------------------------------------------------
    @staticmethod
    def is_trusted_domain(url: str) -> bool:
        """Check if a URL belongs to a trusted official domain."""
        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            return any(
                hostname == domain or hostname.endswith("." + domain)
                for domain in TRUSTED_DOMAINS
            )
        except Exception:
            return False

    @staticmethod
    def validate_source_url(url: str) -> bool:
        """Validate that a URL is well-formed and belongs to a trusted domain."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            if not parsed.hostname:
                return False
            return OfficialSourceService.is_trusted_domain(url)
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Rate limiting (internal)
    # ------------------------------------------------------------------
    def _check_rate_limit(self) -> bool:
        now = time.time()
        self._request_timestamps = [
            t for t in self._request_timestamps if now - t < 60
        ]
        return len(self._request_timestamps) < self._rate_limit_per_minute

    def _record_request(self) -> None:
        self._request_timestamps.append(time.time())

    # ------------------------------------------------------------------
    # Core HTTP fetch with caching
    # ------------------------------------------------------------------
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page from a trusted official domain.
        Returns extracted text content, or None on failure.
        """
        if not self.validate_source_url(url):
            logger.warning(f"[OFFICIAL_SOURCE] Rejected untrusted URL: {url}")
            return None

        # Check cache
        cache_key = hashlib.sha256(url.encode()).hexdigest()
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.info(f"[OFFICIAL_SOURCE] Cache hit for {url}")
            return cached

        # Rate limit check
        if not self._check_rate_limit():
            logger.warning(f"[OFFICIAL_SOURCE] Rate limit exceeded, skipping fetch for {url}")
            return None

        async with self._request_semaphore:
            try:
                self._record_request()
                headers = {
                    "User-Agent": "e-BIS-Sahayak/1.0 (Official BIS Information Retrieval; +https://github.com/ebis-sahayak)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8,ta;q=0.7",
                }
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    verify=self.verify_ssl,
                ) as client:
                    response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    logger.warning(
                        f"[OFFICIAL_SOURCE] HTTP {response.status_code} for {url}"
                    )
                    return None

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    logger.info(f"[OFFICIAL_SOURCE] Non-HTML content type at {url}: {content_type}")
                    return None

                raw_html = response.text
                extracted = self._extract_text_from_html(raw_html)

                if extracted and len(extracted.strip()) > 50:
                    self._cache.set(cache_key, extracted)
                    logger.info(
                        f"[OFFICIAL_SOURCE] Successfully fetched {len(extracted)} chars from {url}"
                    )
                    return extracted
                else:
                    logger.info(f"[OFFICIAL_SOURCE] Insufficient text content from {url}")
                    return None

            except (httpx.TimeoutException, asyncio.TimeoutError):
                logger.warning(f"[OFFICIAL_SOURCE] Timeout fetching {url}")
                return None
            except (httpx.ConnectError, httpx.RequestError) as ce:
                err_str = str(ce)
                cause = getattr(ce, "__cause__", None)
                is_ssl_error = (
                    "CERTIFICATE_VERIFY_FAILED" in err_str
                    or "certificate verify failed" in err_str
                    or "SSLError" in str(type(ce))
                    or (cause is not None and ("CERTIFICATE" in str(cause).upper() or "SSL" in str(type(cause)).upper()))
                )
                if is_ssl_error:
                    logger.error(
                        f"[OFFICIAL_SOURCE] TLS certificate verification failed for {url}: {ce}. Request rejected to ensure transport security."
                    )
                else:
                    logger.warning(f"[OFFICIAL_SOURCE] Connection/Network error for {url}: {ce}")
                return None
            except Exception as e:
                logger.error(f"[OFFICIAL_SOURCE] Error fetching {url}: {str(e)}")
                return None

    # ------------------------------------------------------------------
    # HTML text extraction (lightweight, no heavy dependencies)
    # ------------------------------------------------------------------
    def _extract_text_from_html(self, html: str) -> str:
        """
        Extract readable text from HTML using BeautifulSoup if available,
        falling back to regex-based extraction.
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")

            # Remove non-content tags
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
        except ImportError:
            # Fallback: regex-based extraction
            text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

        # Truncate to max length
        if len(text) > self.max_content_length:
            text = text[: self.max_content_length] + "\n[...content truncated]"

        return text

    # ------------------------------------------------------------------
    # Determine relevant URLs for a query
    # ------------------------------------------------------------------
    def get_relevant_urls(self, query: str, intent: str) -> List[Tuple[str, str]]:
        """
        Returns a list of (url, description) tuples relevant to the query,
        drawn from known official BIS portal endpoints.
        Never fabricates URLs — only returns known, verified endpoints.
        """
        q_lower = query.lower()
        urls: List[Tuple[str, str]] = []

        def matches_any(keywords: List[str]) -> bool:
            for kw in keywords:
                # Use word boundaries so 'isi' doesn't match 'invisible', 'lab' doesn't match 'collaborate'
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, q_lower):
                    return True
            return False

        # IS number lookup
        is_match = re.findall(r'\bIS\s*(\d+)', query, re.IGNORECASE)
        if is_match:
            urls.append((
                BIS_SEARCH_URLS["bismanak_catalog"],
                f"BIS Manak Catalogue — Standard Search for IS {is_match[0]}"
            ))

        # QCO / Quality Control Orders
        if matches_any(["qco", "quality control order", "quality control orders", "mandatory certification", "mandatory order"]):
            urls.append((
                BIS_SEARCH_URLS["qco_orders"],
                "BIS Quality Control Orders (QCO) — Official Portal"
            ))

        # Product Certification general
        if matches_any(["certification", "certify", "isi mark", "scheme-i", "scheme i", "bis license"]):
            urls.append((
                BIS_SEARCH_URLS["product_certification"],
                "BIS Product Certification Overview"
            ))

        # ISI Mark / Scheme-I
        if matches_any(["isi", "isi mark", "scheme-i", "scheme i", "compulsory certification"]):
            urls.append((
                BIS_SEARCH_URLS["isi_scheme"],
                "Products under BIS Compulsory Certification (ISI Mark)"
            ))

        # CRS / Scheme-II
        if matches_any(["crs", "scheme-ii", "scheme ii", "registration scheme", "compulsory registration scheme", "electronics registration"]):
            urls.append((
                BIS_SEARCH_URLS["crs_registration"],
                "BIS Compulsory Registration Scheme (CRS) — Scheme-II"
            ))

        # FMCS / Foreign Manufacturer
        if matches_any(["fmcs", "foreign manufacturer", "foreign manufacturers", "scheme-x", "scheme x"]):
            urls.append((
                BIS_SEARCH_URLS["fmcs_scheme"],
                "BIS FMCS Scheme for Foreign Manufacturers"
            ))

        # Laboratory / Testing
        if matches_any(["lab", "labs", "laboratory", "laboratories", "testing facility", "testing lab", "nabl"]):
            urls.append((
                BIS_SEARCH_URLS["laboratory_overview"],
                "BIS Laboratory Services Overview"
            ))

        # Hallmarking
        if matches_any(["hallmark", "hallmarking", "gold hallmarking", "silver hallmarking"]):
            urls.append((
                BIS_SEARCH_URLS["hallmarking"],
                "BIS Hallmarking Scheme"
            ))

        # License verification
        if matches_any(["verify", "license", "licence", "verify license", "license verification", "verify cml", "cml", "r-number", "check license"]):
            urls.append((
                BIS_SEARCH_URLS["manakonline_verify"],
                "BIS Manakonline — License Verification Portal"
            ))

        # General BIS portal fallback: only when query explicitly asks about BIS or standards
        bis_general_keywords = [
            "bis", "bureau of indian standards", "manakonline", "standards portal",
            "indian standard", "what is bis", "about bis", "ministry", "act",
            "jurisdiction", "functions of bis", "national standards body", "conformity assessment"
        ]
        if intent in ["GENERAL_BIS_INFORMATION"] and matches_any(bis_general_keywords):
            if not urls:
                urls.append((
                    BIS_SEARCH_URLS["bis_portal"],
                    "Bureau of Indian Standards — Official Portal"
                ))

        # Deduplicate
        seen = set()
        unique_urls = []
        for url, desc in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append((url, desc))

        return unique_urls[:4]  # Cap at 4 concurrent lookups

    # ------------------------------------------------------------------
    # High-level evidence retrieval
    # ------------------------------------------------------------------
    async def lookup_evidence(
        self, query: str, intent: str
    ) -> List[OfficialSourceEvidence]:
        """
        Look up official sources relevant to the given query and intent.
        Returns a list of OfficialSourceEvidence items with real fetched content.
        """
        relevant_urls = self.get_relevant_urls(query, intent)
        if not relevant_urls:
            return []

        retrieval_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        evidence_items: List[OfficialSourceEvidence] = []

        # Fetch pages concurrently
        tasks = []
        for url, description in relevant_urls:
            tasks.append(self._fetch_and_build_evidence(url, description, retrieval_date))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, OfficialSourceEvidence):
                evidence_items.append(result)
            elif isinstance(result, Exception):
                logger.error(f"[OFFICIAL_SOURCE] Evidence fetch error: {str(result)}")

        return evidence_items

    async def _fetch_and_build_evidence(
        self, url: str, description: str, retrieval_date: str
    ) -> Optional[OfficialSourceEvidence]:
        """Fetch a single URL and build an evidence item."""
        content = await self.fetch_page(url)
        if not content:
            return None

        parsed = urlparse(url)
        domain = parsed.hostname or ""

        return OfficialSourceEvidence(
            title=description,
            url=url,
            domain=domain,
            retrieved_text=content,
            retrieval_date=retrieval_date,
            source_type="official_bis" if "bis.gov.in" in domain else "official_gov",
            is_verified_domain=True,
        )

    # ------------------------------------------------------------------
    # Format evidence for Groq context injection
    # ------------------------------------------------------------------
    @staticmethod
    def format_evidence_for_groq(
        evidence_items: List[OfficialSourceEvidence],
    ) -> str:
        """
        Format retrieved official-source evidence into a structured text block
        suitable for injection into the Groq system/user prompt.
        """
        if not evidence_items:
            return ""

        lines = ["--- OFFICIAL SOURCE EVIDENCE (Retrieved from verified Government of India portals) ---"]
        for idx, item in enumerate(evidence_items, 1):
            lines.append(f"\nOFFICIAL SOURCE {idx}:")
            lines.append(f"  Title: {item.title}")
            lines.append(f"  URL: {item.url}")
            lines.append(f"  Domain: {item.domain}")
            lines.append(f"  Retrieved: {item.retrieval_date}")
            # Limit per-source text to prevent token overflow
            text_snippet = item.retrieved_text[:3000]
            if len(item.retrieved_text) > 3000:
                text_snippet += "\n  [...additional content truncated for token efficiency]"
            lines.append(f"  Content:\n{text_snippet}")
        lines.append("\n--- END OFFICIAL SOURCE EVIDENCE ---")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------
    def clear_cache(self) -> int:
        """Clear the evidence cache. Returns the number of entries cleared."""
        size = self._cache.size
        self._cache.clear()
        return size

    @property
    def cache_size(self) -> int:
        return self._cache.size


# Module-level singleton
official_source_service = OfficialSourceService()
