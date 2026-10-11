"""
Tests for OfficialSourceService — Lightweight official-source evidence lookup.
Covers domain validation, URL relevance mapping, caching, rate limiting,
HTML extraction, and evidence formatting.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.official_source_service import (
    OfficialSourceService,
    OfficialSourceEvidence,
    TTLCache,
    TRUSTED_DOMAINS,
    BIS_SEARCH_URLS,
)


# ===========================================================================
# Domain Validation Tests
# ===========================================================================

class TestDomainValidation:
    """Tests for trusted domain validation."""

    def test_trusted_bis_gov_in(self):
        assert OfficialSourceService.is_trusted_domain("https://bis.gov.in/index.php/product-certification/")

    def test_trusted_www_bis_gov_in(self):
        assert OfficialSourceService.is_trusted_domain("https://www.bis.gov.in/some-page")

    def test_trusted_services_bis_gov_in(self):
        assert OfficialSourceService.is_trusted_domain("https://services.bis.gov.in/php/BIS_2/bismanak/index.php")

    def test_trusted_standards_bis_gov_in(self):
        assert OfficialSourceService.is_trusted_domain("https://standards.bis.gov.in/catalog")

    def test_trusted_manakonline(self):
        assert OfficialSourceService.is_trusted_domain("https://manakonline.in/MANAK/SearchLicence")

    def test_trusted_egazette(self):
        assert OfficialSourceService.is_trusted_domain("https://egazette.gov.in/notification/123")

    def test_trusted_india_gov_in(self):
        assert OfficialSourceService.is_trusted_domain("https://india.gov.in/")

    def test_untrusted_google(self):
        assert not OfficialSourceService.is_trusted_domain("https://www.google.com/search?q=bis")

    def test_untrusted_wikipedia(self):
        assert not OfficialSourceService.is_trusted_domain("https://en.wikipedia.org/wiki/Bureau_of_Indian_Standards")

    def test_untrusted_random_site(self):
        assert not OfficialSourceService.is_trusted_domain("https://some-random-site.com/fake-bis-info")

    def test_untrusted_spoofed_domain(self):
        assert not OfficialSourceService.is_trusted_domain("https://bis.gov.in.fake-domain.com/phishing")

    def test_empty_url(self):
        assert not OfficialSourceService.is_trusted_domain("")

    def test_malformed_url(self):
        assert not OfficialSourceService.is_trusted_domain("not-a-url")

    def test_validate_source_url_valid(self):
        assert OfficialSourceService.validate_source_url("https://bis.gov.in/index.php/product-certification/")

    def test_validate_source_url_http(self):
        assert OfficialSourceService.validate_source_url("http://bis.gov.in")

    def test_validate_source_url_ftp_rejected(self):
        assert not OfficialSourceService.validate_source_url("ftp://bis.gov.in/files")

    def test_validate_source_url_no_scheme(self):
        assert not OfficialSourceService.validate_source_url("bis.gov.in/index.php")


# ===========================================================================
# URL Relevance Mapping Tests
# ===========================================================================

class TestURLRelevanceMapping:
    """Tests for query-to-URL mapping logic."""

    def setup_method(self):
        self.service = OfficialSourceService()

    def test_standard_number_triggers_catalog(self):
        urls = self.service.get_relevant_urls("What is IS 17803?", "STANDARD_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("bismanak" in u for u in url_list)

    def test_qco_query_triggers_qco_page(self):
        urls = self.service.get_relevant_urls("Is QCO mandatory for ceiling fans?", "QCO_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("quality-control-orders" in u for u in url_list)

    def test_certification_query_triggers_cert_page(self):
        urls = self.service.get_relevant_urls("How to get ISI Mark certification?", "CERTIFICATION_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("product-certification" in u for u in url_list)

    def test_crs_query_triggers_crs_page(self):
        urls = self.service.get_relevant_urls("CRS registration for electronics", "CERTIFICATION_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("scheme-ii" in u for u in url_list)

    def test_fmcs_query_triggers_fmcs_page(self):
        urls = self.service.get_relevant_urls("FMCS scheme for foreign manufacturer", "CERTIFICATION_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("fmcs" in u.lower() for u in url_list)

    def test_lab_query_triggers_lab_page(self):
        urls = self.service.get_relevant_urls("testing laboratory for water bottles", "LABORATORY_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("laboratory" in u for u in url_list)

    def test_hallmark_query_triggers_hallmark_page(self):
        urls = self.service.get_relevant_urls("hallmarking of gold", "CERTIFICATION_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("hallmarking" in u for u in url_list)

    def test_verify_query_triggers_manakonline(self):
        urls = self.service.get_relevant_urls("verify BIS license", "GENERAL_BIS_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("manakonline" in u for u in url_list)

    def test_general_query_gets_bis_portal(self):
        urls = self.service.get_relevant_urls("what is BIS", "GENERAL_BIS_INFORMATION")
        url_list = [u for u, _ in urls]
        assert any("bis.gov.in" in u for u in url_list)

    def test_max_4_urls(self):
        urls = self.service.get_relevant_urls(
            "ISI mark certification CRS FMCS QCO hallmark laboratory verify",
            "GENERAL_BIS_INFORMATION"
        )
        assert len(urls) <= 4

    def test_no_duplicate_urls(self):
        urls = self.service.get_relevant_urls("CRS registration scheme", "CERTIFICATION_INFORMATION")
        url_list = [u for u, _ in urls]
        assert len(url_list) == len(set(url_list))


# ===========================================================================
# TTL Cache Tests
# ===========================================================================

class TestTTLCache:
    """Tests for the in-memory TTL cache."""

    def test_set_and_get(self):
        cache = TTLCache(default_ttl_seconds=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_expired_entry(self):
        cache = TTLCache(default_ttl_seconds=0)
        cache.set("key1", "value1", ttl=0)
        import time
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_custom_ttl(self):
        cache = TTLCache(default_ttl_seconds=0)
        cache.set("key1", "value1", ttl=3600)
        assert cache.get("key1") == "value1"

    def test_max_entries_eviction(self):
        cache = TTLCache(default_ttl_seconds=3600, max_entries=3)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.set("k4", "v4")  # Should evict oldest
        assert cache.size <= 3

    def test_clear(self):
        cache = TTLCache()
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.size == 0
        assert cache.get("k1") is None


# ===========================================================================
# HTML Extraction Tests
# ===========================================================================

class TestHTMLExtraction:
    """Tests for text extraction from HTML content."""

    def setup_method(self):
        self.service = OfficialSourceService()

    def test_basic_html_extraction(self):
        html = "<html><body><h1>Title</h1><p>Content paragraph.</p></body></html>"
        result = self.service._extract_text_from_html(html)
        assert "Title" in result
        assert "Content paragraph" in result

    def test_script_removal(self):
        html = "<html><body><script>alert('xss')</script><p>Real content.</p></body></html>"
        result = self.service._extract_text_from_html(html)
        assert "alert" not in result
        assert "Real content" in result

    def test_style_removal(self):
        html = "<html><head><style>.cls{color:red}</style></head><body><p>Visible text.</p></body></html>"
        result = self.service._extract_text_from_html(html)
        assert "color:red" not in result
        assert "Visible text" in result

    def test_nav_footer_removal(self):
        html = "<html><body><nav>Menu items</nav><main><p>Main content here.</p></main><footer>Footer text</footer></body></html>"
        result = self.service._extract_text_from_html(html)
        assert "Main content here" in result

    def test_truncation(self):
        service = OfficialSourceService(max_content_length=50)
        html = f"<html><body><p>{'A' * 200}</p></body></html>"
        result = service._extract_text_from_html(html)
        assert len(result) < 200
        assert "truncated" in result


# ===========================================================================
# Evidence Formatting Tests
# ===========================================================================

class TestEvidenceFormatting:
    """Tests for Groq evidence formatting."""

    def test_format_empty_evidence(self):
        result = OfficialSourceService.format_evidence_for_groq([])
        assert result == ""

    def test_format_single_evidence(self):
        evidence = [
            OfficialSourceEvidence(
                title="Test Source",
                url="https://bis.gov.in/test",
                domain="bis.gov.in",
                retrieved_text="Sample text content",
                retrieval_date="2026-10-04 06:00 UTC",
            )
        ]
        result = OfficialSourceService.format_evidence_for_groq(evidence)
        assert "OFFICIAL SOURCE 1:" in result
        assert "Test Source" in result
        assert "bis.gov.in" in result
        assert "2026-10-04" in result
        assert "Sample text content" in result

    def test_format_multiple_evidence(self):
        evidence = [
            OfficialSourceEvidence(
                title=f"Source {i}",
                url=f"https://bis.gov.in/page{i}",
                domain="bis.gov.in",
                retrieved_text=f"Content {i}",
                retrieval_date="2026-10-04",
            )
            for i in range(3)
        ]
        result = OfficialSourceService.format_evidence_for_groq(evidence)
        assert "OFFICIAL SOURCE 1:" in result
        assert "OFFICIAL SOURCE 2:" in result
        assert "OFFICIAL SOURCE 3:" in result


# ===========================================================================
# OfficialSourceEvidence Tests
# ===========================================================================

class TestOfficialSourceEvidence:
    """Tests for evidence data class."""

    def test_to_dict(self):
        ev = OfficialSourceEvidence(
            title="BIS Portal",
            url="https://bis.gov.in",
            domain="bis.gov.in",
            retrieved_text="Some text",
            retrieval_date="2026-10-04",
            source_type="official_bis",
            is_verified_domain=True,
        )
        d = ev.to_dict()
        assert d["title"] == "BIS Portal"
        assert d["url"] == "https://bis.gov.in"
        assert d["domain"] == "bis.gov.in"
        assert d["is_verified_domain"] is True

    def test_default_source_type(self):
        ev = OfficialSourceEvidence(
            title="Test", url="https://bis.gov.in", domain="bis.gov.in",
            retrieved_text="text", retrieval_date="2026-01-01",
        )
        assert ev.source_type == "official_bis"


# ===========================================================================
# Rate Limiting Tests
# ===========================================================================

class TestRateLimiting:
    """Tests for internal rate limiting."""

    def test_rate_limit_allows_initial_requests(self):
        service = OfficialSourceService()
        assert service._check_rate_limit() is True

    def test_rate_limit_blocks_after_limit(self):
        service = OfficialSourceService()
        service._rate_limit_per_minute = 5
        for _ in range(5):
            service._record_request()
        assert service._check_rate_limit() is False


# ===========================================================================
# Fetch Page Tests (mocked HTTP)
# ===========================================================================

class TestFetchPage:
    """Tests for page fetching with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_fetch_untrusted_url_returns_none(self):
        service = OfficialSourceService()
        result = await service.fetch_page("https://untrusted-site.com/page")
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_uses_cache(self):
        service = OfficialSourceService()
        # Pre-populate cache
        import hashlib
        url = "https://bis.gov.in/test-page"
        cache_key = hashlib.sha256(url.encode()).hexdigest()
        service._cache.set(cache_key, "Cached content")

        result = await service.fetch_page(url)
        assert result == "Cached content"

    @pytest.mark.asyncio
    async def test_fetch_page_returns_none_on_rate_limit(self):
        service = OfficialSourceService()
        service._rate_limit_per_minute = 0  # Block all
        result = await service.fetch_page("https://bis.gov.in/test")
        assert result is None


# ===========================================================================
# Integration: lookup_evidence Tests
# ===========================================================================

class TestLookupEvidence:
    """Tests for the high-level lookup_evidence method."""

    @pytest.mark.asyncio
    async def test_lookup_with_no_relevant_urls(self):
        service = OfficialSourceService()
        # A query that produces no matching URLs
        result = await service.lookup_evidence("random garbage text", "OUT_OF_SCOPE")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_lookup_returns_list_of_evidence(self):
        service = OfficialSourceService()
        # Mock fetch_page to return content
        async def mock_fetch(url):
            return "BIS certification details for ISI mark scheme-I."

        with patch.object(service, 'fetch_page', side_effect=mock_fetch):
            result = await service.lookup_evidence("ISI mark certification", "CERTIFICATION_INFORMATION")
            assert isinstance(result, list)
            if result:
                assert isinstance(result[0], OfficialSourceEvidence)
                assert result[0].is_verified_domain is True


# ===========================================================================
# Cache Management Tests
# ===========================================================================

class TestCacheManagement:
    """Tests for cache management methods."""

    def test_clear_cache(self):
        service = OfficialSourceService()
        service._cache.set("k1", "v1")
        service._cache.set("k2", "v2")
        cleared = service.clear_cache()
        assert cleared == 2
        assert service.cache_size == 0

    def test_cache_size_property(self):
        service = OfficialSourceService()
        assert service.cache_size == 0
        service._cache.set("k1", "v1")
        assert service.cache_size == 1


# ===========================================================================
# Trusted Domain Completeness Tests
# ===========================================================================

class TestTrustedDomainCompleteness:
    """Verify all expected official domains are in the whitelist."""

    def test_bis_gov_in_in_list(self):
        assert "bis.gov.in" in TRUSTED_DOMAINS

    def test_services_bis_in_list(self):
        assert "services.bis.gov.in" in TRUSTED_DOMAINS

    def test_standards_bis_in_list(self):
        assert "standards.bis.gov.in" in TRUSTED_DOMAINS

    def test_manakonline_in_list(self):
        assert "manakonline.in" in TRUSTED_DOMAINS

    def test_egazette_in_list(self):
        assert "egazette.gov.in" in TRUSTED_DOMAINS


# ===========================================================================
# BIS Search URLs Completeness Tests
# ===========================================================================

class TestBISSearchURLs:
    """Verify BIS search URL map completeness."""

    def test_all_urls_are_trusted(self):
        service = OfficialSourceService()
        for key, url in BIS_SEARCH_URLS.items():
            assert service.validate_source_url(url), f"BIS_SEARCH_URLS['{key}'] = '{url}' is not a trusted URL"

    def test_standard_search_exists(self):
        assert "bismanak_catalog" in BIS_SEARCH_URLS

    def test_qco_orders_exists(self):
        assert "qco_orders" in BIS_SEARCH_URLS

    def test_product_certification_exists(self):
        assert "product_certification" in BIS_SEARCH_URLS


# ===========================================================================
# TLS Security & Certificate Verification Tests
# ===========================================================================

class TestTLSSecurityAndVerification:
    """Tests confirming TLS verification is strictly enabled and fails closed."""

    def test_default_verify_ssl_is_true(self):
        service = OfficialSourceService()
        assert service.verify_ssl is True

    @pytest.mark.asyncio
    async def test_httpx_client_receives_verify_flag(self):
        service = OfficialSourceService(verify_ssl=True)
        captured_kwargs = {}

        class MockAsyncClient:
            def __init__(self, *args, **kwargs):
                nonlocal captured_kwargs
                captured_kwargs = kwargs

            async def __aenter__(self):
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.headers = {"content-type": "text/html"}
                mock_resp.text = "<html><body><h1>Bureau of Indian Standards</h1><p>Comprehensive official details regarding BIS certification schemes, processes, and licensing requirements across India.</p></body></html>"
                self.get = AsyncMock(return_value=mock_resp)
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        with patch("httpx.AsyncClient", side_effect=MockAsyncClient):
            content = await service.fetch_page("https://bis.gov.in/index.php/product-certification/")
            assert content is not None
            assert captured_kwargs.get("verify") is True
            assert captured_kwargs.get("follow_redirects") is True

    @pytest.mark.asyncio
    async def test_tls_ssl_error_fails_closed(self):
        import ssl
        service = OfficialSourceService(verify_ssl=True)

        class MockFailingAsyncClient:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                mock_inst = MagicMock()
                ssl_err = ssl.SSLCertVerificationError("certificate verify failed: self-signed certificate")
                mock_inst.get = AsyncMock(side_effect=httpx.ConnectError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed", request=MagicMock()))
                return mock_inst

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        with patch("httpx.AsyncClient", side_effect=MockFailingAsyncClient):
            result = await service.fetch_page("https://bis.gov.in/index.php/product-certification/")
            # Must fail closed and return None
            assert result is None

    @pytest.mark.asyncio
    async def test_timeout_fails_gracefully(self):
        service = OfficialSourceService(verify_ssl=True)

        class MockTimeoutAsyncClient:
            def __init__(self, *args, **kwargs):
                pass

            async def __aenter__(self):
                mock_inst = MagicMock()
                mock_inst.get = AsyncMock(side_effect=httpx.TimeoutException("Connection timed out"))
                return mock_inst

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        with patch("httpx.AsyncClient", side_effect=MockTimeoutAsyncClient):
            result = await service.fetch_page("https://bis.gov.in/index.php/product-certification/")
            assert result is None


# ===========================================================================
# Laboratory Importer TLS Verification Tests
# ===========================================================================

class TestLabImporterTLSSecurity:
    """Tests confirming import_laboratories.py uses secure TLS verification."""

    def test_fetch_url_html_ssl_error_fails_closed(self):
        import ssl
        from app.scripts.import_laboratories import fetch_url_html

        ssl_err = ssl.SSLCertVerificationError("certificate verify failed")
        with patch("urllib.request.urlopen", side_effect=ssl_err):
            result = fetch_url_html("https://lims.bis.gov.in/labs")
            assert result is None

    def test_fetch_url_html_success(self):
        from app.scripts.import_laboratories import fetch_url_html

        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<html><body><table><tr><td>Sample Lab</td></tr></table></body></html>"
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = fetch_url_html("https://lims.bis.gov.in/labs")
            assert result is not None
            assert "Sample Lab" in result

    def test_fetch_url_html_creates_secure_context(self):
        import ssl
        from app.scripts.import_laboratories import fetch_url_html

        with patch("ssl.create_default_context") as mock_ctx_factory:
            mock_ctx = MagicMock()
            mock_ctx_factory.return_value = mock_ctx
            with patch("urllib.request.urlopen"):
                fetch_url_html("https://lims.bis.gov.in/labs")
                assert mock_ctx.check_hostname is True
                assert mock_ctx.verify_mode == ssl.CERT_REQUIRED

