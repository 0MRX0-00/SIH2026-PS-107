"""
Seed BIS Data Provider.
Provides structured querying for Indian Standards, certification schemes, and laboratories
using the verified in-memory registry with explicit data provenance, source priority,
and claim verification metadata.
"""
from typing import List, Dict, Any, Optional
from app.services.data_providers.base_provider import BaseBISDataProvider
from app.schemas.chat import SourceItem
from app.schemas.intelligence import (
    StandardListItem,
    StandardDetailResponse,
    StandardSectionItem,
    LaboratoryItem,
    LaboratorySearchResponse,
    LaboratorySearchRequest,
    CandidateStandardItem
)
from app.db.seed_intelligence import (
    VERIFIED_STANDARDS,
    VERIFIED_SCHEMES,
    VERIFIED_LABORATORIES,
    get_localized_standard,
    get_localized_all_standards,
    get_localized_scheme,
    get_localized_all_schemes,
    get_localized_laboratory,
    get_localized_all_laboratories
)


class SeedBISDataProvider(BaseBISDataProvider):
    """Seed / In-Memory implementation of BaseBISDataProvider with explicit provenance."""

    def get_evidence_provenance(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract explicit data provenance metadata for a record with claim integrity validation."""
        is_verified = record.get("verified", True)
        url = record.get("source_url", "https://bis.gov.in")

        # Invalidate status if URL is invalid or marked unverified
        if not is_verified or not url or not url.startswith("http"):
            v_status = "unverified"
            is_verified = False
        else:
            v_status = record.get("verification_status", "authoritative_curated")

        return {
            "title": record.get("title") or record.get("standard_number") or record.get("lab_name"),
            "standard_number": record.get("standard_number"),
            "source_url": url,
            "source_type": record.get("source_type", "official_bis"),
            "authority": record.get("authority", "Bureau of Indian Standards"),
            "verified": is_verified,
            "verification_status": v_status,
            "provenance": record.get("provenance", "Official BIS Gazette Notification & Catalog Registry"),
            "last_verified": record.get("last_verified", "2026-01-15"),
            "source_priority": record.get("source_priority", 1),
            "evidence_scope": record.get("evidence_scope", "Official specification and regulatory scope"),
            "supported_claims": record.get("supported_claims", ["standard_existence"])
        }

    def search_standards(
        self,
        query: Optional[str] = None,
        division: Optional[str] = None,
        qco_only: Optional[bool] = None,
        limit: int = 50,
        language: str = "en"
    ) -> List[StandardListItem]:
        results: List[StandardListItem] = []
        q_lower = (query or "").strip().lower()
        div_lower = (division or "").strip().lower()

        localized_list = get_localized_all_standards(language)

        for std, orig_std in zip(localized_list, VERIFIED_STANDARDS):
            if division:
                if div_lower not in orig_std["division"].lower() and div_lower not in std["division"].lower():
                    continue

            if qco_only is not None and orig_std["is_qco_mandatory"] != qco_only:
                continue

            if q_lower:
                searchable = f"{std['standard_number']} {std['title']} {std['division']} {std.get('scope_summary', '')}".lower()
                if q_lower not in searchable:
                    continue

            results.append(StandardListItem(
                id=std["id"],
                standard_number=std["standard_number"],
                title=std["title"],
                division=std["division"],
                year=std.get("year"),
                status=std["status"],
                is_qco_mandatory=std["is_qco_mandatory"],
                scope_summary=std.get("scope_summary")
            ))

        return results[:limit]

    def get_standard_details(
        self,
        standard_id_or_number: str,
        language: str = "en"
    ) -> Optional[StandardDetailResponse]:
        lookup = standard_id_or_number.strip().lower()
        lookup_norm = lookup.replace("-", " ").replace(":", " ")

        matched_idx = next(
            (
                idx for idx, s in enumerate(VERIFIED_STANDARDS)
                if s["id"].lower() == lookup
                or lookup in s["standard_number"].lower()
                or s["standard_number"].lower() == lookup
                or lookup in s["standard_number"].replace(" ", "").lower()
                or lookup.replace("-", "") in s["standard_number"].replace(" ", "").replace(":", "").lower()
                or any(w in s["standard_number"].lower() for w in lookup_norm.split() if w.isdigit())
            ),
            None
        )

        if matched_idx is None:
            return None

        orig_matched = VERIFIED_STANDARDS[matched_idx]
        matched = get_localized_standard(orig_matched, language)

        sections = [
            StandardSectionItem(
                clause_number=sec["clause_number"],
                clause_title=sec.get("clause_title"),
                content=sec["content"],
                page_number=sec.get("page_number")
            )
            for sec in matched.get("sections", [])
        ]

        return StandardDetailResponse(
            id=matched["id"],
            standard_number=matched["standard_number"],
            title=matched["title"],
            division=matched["division"],
            year=matched.get("year"),
            status=matched["status"],
            is_qco_mandatory=matched["is_qco_mandatory"],
            qco_order_number=matched.get("qco_order_number"),
            scope_summary=matched.get("scope_summary"),
            sections=sections,
            related_standards=matched.get("related_standards", [])
        )

    def discover_product_standards(
        self,
        product_description: str,
        material: Optional[str] = None,
        intended_use: Optional[str] = None,
        max_candidates: int = 5,
        language: str = "en"
    ) -> List[CandidateStandardItem]:
        desc = (product_description or "").strip().lower()
        if not desc:
            return []

        candidates: List[CandidateStandardItem] = []
        search_terms = set(desc.split())
        if material:
            search_terms.add(material.lower())
        if intended_use:
            search_terms.add(intended_use.lower())

        for reg in VERIFIED_STANDARDS:
            std_num = reg["standard_number"]
            title = reg["title"]
            scope = reg.get("scope_summary", "")
            full_text = f"{std_num} {title} {scope}".lower()

            match_count = sum(1 for t in search_terms if len(t) > 2 and t in full_text)
            if match_count > 0:
                is_qco = reg.get("is_qco_mandatory", False)
                qco_order = reg.get("qco_order_number")
                schemes = ["Scheme-I (ISI Mark)"]
                if "CRS" in title or "CRS" in scope or "IS 16046" in std_num or "IS 13252" in std_num:
                    schemes = ["Scheme-II (CRS)"]

                prov = self.get_evidence_provenance(reg)
                sources_list = [
                    SourceItem(
                        title=f"{std_num} - {title}",
                        url=prov["source_url"],
                        source_type=prov["source_type"],
                        authority=prov["authority"],
                        verified=prov["verified"],
                        verification_status=prov["verification_status"],
                        provenance=prov["provenance"],
                        last_verified=prov["last_verified"],
                        source_priority=prov["source_priority"]
                    )
                ]

                candidates.append(
                    CandidateStandardItem(
                        standard_number=std_num,
                        title=title,
                        relevance_reason=f"Matches product description '{product_description}' under {reg['division']} division.",
                        evidence_status="VERIFIED" if prov["verified"] else "UNVERIFIED",
                        is_mandatory_qco=is_qco,
                        qco_details=qco_order,
                        applicable_schemes=schemes,
                        applicability_caveat="Verify specific model rated parameters against BIS gazette notifications.",
                        citations=sources_list
                    )
                )

        return candidates[:max_candidates]

    def search_laboratories(self, request: LaboratorySearchRequest) -> LaboratorySearchResponse:
        results: List[LaboratoryItem] = []
        q_lower = (request.query or "").strip().lower()
        city_lower = (request.city or "").strip().lower()
        state_lower = (request.state or "").strip().lower()
        std_lower = (request.standard_number or "").strip().lower()
        recog_lower = (request.recognition_type or "").strip().lower()
        lang = request.language or "en"

        localized_labs = get_localized_all_laboratories(lang)

        product_std_map = {
            "fan": "17803",
            "ceiling fan": "17803",
            "electric fan": "17803",
            "plug": "1293",
            "socket": "1293",
            "water": "14543",
            "bottle": "14543",
            "drinking water": "14543",
            "laptop": "13252",
            "computer": "13252",
            "electronics": "13252",
            "it equipment": "13252",
        }

        mapped_std = None
        if q_lower:
            for prod_k, std_v in product_std_map.items():
                if prod_k in q_lower:
                    mapped_std = std_v
                    break

        for lab, orig_lab in zip(localized_labs, VERIFIED_LABORATORIES):
            if city_lower and city_lower not in orig_lab["city"].lower() and city_lower not in lab["city"].lower():
                continue

            if state_lower and state_lower not in orig_lab["state"].lower() and state_lower not in lab["state"].lower():
                continue

            if recog_lower and recog_lower not in orig_lab["recognition_type"].lower():
                continue

            if std_lower:
                std_match = any(std_lower in acc_std.lower() for acc_std in orig_lab["accredited_standards"])
                if not std_match:
                    continue

            if q_lower:
                searchable = f"{lab['lab_name']} {lab['city']} {lab['state']} {lab.get('testing_scope_summary', '')} {orig_lab['lab_name']} {' '.join(orig_lab['accredited_standards'])}".lower()
                has_match = (q_lower in searchable)
                if not has_match and mapped_std:
                    has_match = any(mapped_std in acc_std for acc_std in orig_lab["accredited_standards"])
                if not has_match:
                    tokens = [t for t in q_lower.split() if len(t) > 3 and t not in ["which", "what", "where", "test", "my", "product", "laboratory", "laboratories", "lab", "labs", "can"]]
                    if tokens:
                        has_match = any(t in searchable for t in tokens)

                if not has_match:
                    continue

            results.append(LaboratoryItem(
                id=lab["id"],
                lab_name=lab["lab_name"],
                lab_code=lab.get("lab_code"),
                recognition_type=lab["recognition_type"],
                city=lab["city"],
                state=lab["state"],
                address=lab.get("address"),
                contact_details=lab.get("contact_details"),
                testing_scope_summary=lab.get("testing_scope_summary"),
                accredited_standards=lab.get("accredited_standards", [])
            ))

        return LaboratorySearchResponse(
            total_count=len(results),
            laboratories=results[:request.limit]
        )

    def list_all_laboratories(self, language: str = "en") -> List[LaboratoryItem]:
        localized_labs = get_localized_all_laboratories(language)
        return [
            LaboratoryItem(
                id=lab["id"],
                lab_name=lab["lab_name"],
                lab_code=lab.get("lab_code"),
                recognition_type=lab["recognition_type"],
                city=lab["city"],
                state=lab["state"],
                address=lab.get("address"),
                contact_details=lab.get("contact_details"),
                testing_scope_summary=lab.get("testing_scope_summary"),
                accredited_standards=lab.get("accredited_standards", [])
            )
            for lab in localized_labs
        ]

    def list_all_schemes(self, language: str = "en") -> List[Dict[str, Any]]:
        return get_localized_all_schemes(language)
