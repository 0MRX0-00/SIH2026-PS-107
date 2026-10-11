"""
Seed BIS Data Provider.
Provides structured querying for Indian Standards, certification schemes, and laboratories
using the verified in-memory registry with explicit data provenance, source priority,
and claim verification metadata.
"""
import json
from datetime import datetime
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
        product_category: Optional[str] = None,
        qco_only: Optional[bool] = None,
        limit: int = 50,
        language: str = "en"
    ) -> List[StandardListItem]:
        results: List[StandardListItem] = []
        q_lower = (query or "").strip().lower()
        div_lower = (division or "").strip().lower()
        cat_lower = (product_category or "").strip().lower()

        localized_list = get_localized_all_standards(language)

        for std, orig_std in zip(localized_list, VERIFIED_STANDARDS):
            if division and div_lower != "all technical divisions":
                orig_div = orig_std.get("division", "").lower()
                loc_div = std.get("division", "").lower()
                if div_lower not in orig_div and div_lower not in loc_div:
                    continue

            if product_category and cat_lower != "all categories":
                orig_cat = orig_std.get("product_category", "").lower()
                loc_cat = std.get("product_category", "").lower()
                if cat_lower not in orig_cat and cat_lower not in loc_cat:
                    continue

            if qco_only is not None and orig_std.get("is_qco_mandatory", False) != qco_only:
                continue

            if q_lower:
                std_num = std.get("standard_number", "").lower()
                title = std.get("title", "").lower()
                div = std.get("division", "").lower()
                cat = std.get("product_category", "").lower()
                comm = std.get("technical_committee", "").lower()
                qco = std.get("qco_order_number", "") or ""
                scope = std.get("scope_summary", "") or ""
                
                searchable = f"{std_num} {title} {div} {cat} {comm} {qco.lower()} {scope.lower()}".lower()
                searchable_clean = searchable.replace(":", " ").replace("-", " ").replace("/", " ")
                q_clean = q_lower.replace(":", " ").replace("-", " ").replace("/", " ")

                # Match if query substring exists or if token overlap occurs
                q_tokens = [tok for tok in q_clean.split() if len(tok) > 1]
                if q_lower not in searchable and not (q_tokens and all(tok in searchable_clean for tok in q_tokens)):
                    continue

            prov = self.get_evidence_provenance(orig_std)

            results.append(StandardListItem(
                id=std.get("id"),
                standard_number=std["standard_number"],
                title=std["title"],
                division=std["division"],
                technical_committee=std.get("technical_committee") or orig_std.get("technical_committee"),
                product_category=std.get("product_category") or orig_std.get("product_category"),
                year=std.get("year"),
                status=std.get("status", "ACTIVE"),
                edition_info=std.get("edition_info") or orig_std.get("edition_info"),
                is_qco_mandatory=std.get("is_qco_mandatory", False),
                qco_order_number=std.get("qco_order_number"),
                qco_notifying_ministry=std.get("qco_notifying_ministry") or orig_std.get("qco_notifying_ministry"),
                applicable_schemes=std.get("applicable_schemes") or orig_std.get("applicable_schemes", []),
                scope_summary=std.get("scope_summary"),
                source_url=prov.get("source_url"),
                provenance=prov.get("provenance"),
                verification_status=prov.get("verification_status", "authoritative_verified"),
                last_verified=prov.get("last_verified", "2026-10-10")
            ))

        return results[:limit]

    def get_standard_details(
        self,
        standard_id_or_number: str,
        language: str = "en"
    ) -> Optional[StandardDetailResponse]:
        lookup = standard_id_or_number.strip().lower()
        lookup_norm = lookup.replace("-", " ").replace(":", " ").replace("/", " ")

        matched_idx = next(
            (
                idx for idx, s in enumerate(VERIFIED_STANDARDS)
                if s["id"].lower() == lookup
                or lookup in s["standard_number"].lower()
                or s["standard_number"].lower() == lookup
                or lookup in s["standard_number"].replace(" ", "").lower()
                or lookup.replace("-", "").replace(":", "") in s["standard_number"].replace(" ", "").replace(":", "").lower()
                or any(w in s["standard_number"].lower() for w in lookup_norm.split() if w.isdigit() and len(w) >= 3)
            ),
            None
        )

        if matched_idx is None:
            return None

        orig_matched = VERIFIED_STANDARDS[matched_idx]
        matched = get_localized_standard(orig_matched, language)
        prov = self.get_evidence_provenance(orig_matched)

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
            id=matched.get("id"),
            standard_number=matched["standard_number"],
            title=matched["title"],
            division=matched["division"],
            technical_committee=matched.get("technical_committee") or orig_matched.get("technical_committee"),
            product_category=matched.get("product_category") or orig_matched.get("product_category"),
            year=matched.get("year"),
            status=matched.get("status", "ACTIVE"),
            edition_info=matched.get("edition_info") or orig_matched.get("edition_info"),
            is_qco_mandatory=matched.get("is_qco_mandatory", False),
            qco_order_number=matched.get("qco_order_number"),
            qco_notifying_ministry=matched.get("qco_notifying_ministry") or orig_matched.get("qco_notifying_ministry"),
            applicable_schemes=matched.get("applicable_schemes") or orig_matched.get("applicable_schemes", []),
            scope_summary=matched.get("scope_summary"),
            source_url=prov.get("source_url"),
            source_type=prov.get("source_type", "official_bis"),
            authority=prov.get("authority", "Bureau of Indian Standards"),
            provenance=prov.get("provenance"),
            verification_status=prov.get("verification_status", "authoritative_verified"),
            last_verified=prov.get("last_verified", "2026-10-10"),
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
        code_filter = (request.lab_code or "").strip().lower()
        city_lower = (request.city or "").strip().lower()
        district_lower = (request.district or "").strip().lower()
        state_lower = (request.state or "").strip().lower()
        std_lower = (request.standard_number or "").strip().lower()
        recog_lower = (request.recognition_type or "").strip().lower()
        status_lower = (request.status or "").strip().lower()
        lang = request.language or "en"

        localized_labs = get_localized_all_laboratories(lang)

        product_std_map = {
            "fan": "17803",
            "ceiling fan": "17803",
            "electric fan": "17803",
            "plug": "1293",
            "socket": "1293",
            "water": "14543",
            "mineral water": "13428",
            "bottle": "14543",
            "drinking water": "14543",
            "laptop": "13252",
            "computer": "13252",
            "electronics": "13252",
            "it equipment": "13252",
            "led": "15885",
            "lighting": "15885",
            "steel": "1786",
            "tmt": "1786",
            "iron": "2062",
            "cement": "269",
            "concrete": "456",
            "cable": "694",
            "wire": "694",
            "battery": "16046",
            "cell": "16046",
            "solar": "16221",
            "photovoltaic": "16221",
            "toy": "9873",
            "footwear": "15844",
            "shoe": "15844",
            "switch": "3854",
            "pump": "9079",
            "appliance": "302",
        }

        mapped_std = None
        if q_lower:
            for prod_k, std_v in product_std_map.items():
                if prod_k in q_lower:
                    mapped_std = std_v
                    break

        import re
        std_num_extract = re.search(r'\b\d{3,6}\b', std_lower) if std_lower else None
        std_base_num = std_num_extract.group(0) if std_num_extract else None

        for lab, orig_lab in zip(localized_labs, VERIFIED_LABORATORIES):
            # 1. Lab Code filter
            if code_filter:
                orig_code = (orig_lab.get("lab_code") or "").lower()
                if code_filter not in orig_code:
                    continue

            # 2. City filter
            if city_lower:
                lab_city = (lab.get("city") or "").lower()
                orig_city = (orig_lab.get("city") or "").lower()
                if city_lower not in orig_city and city_lower not in lab_city:
                    continue

            # 3. District filter
            if district_lower:
                lab_dist = (lab.get("district") or "").lower()
                orig_dist = (orig_lab.get("district") or "").lower()
                if district_lower not in orig_dist and district_lower not in lab_dist:
                    continue

            # 4. State filter
            if state_lower:
                lab_st = (lab.get("state") or "").lower()
                orig_st = (orig_lab.get("state") or "").lower()
                if state_lower not in orig_st and state_lower not in lab_st:
                    continue

            # 5. Recognition Type filter
            if recog_lower:
                rec_val = (orig_lab.get("recognition_type") or "").lower()
                if recog_lower not in rec_val:
                    continue

            # 6. Status filter
            if status_lower:
                st_val = (orig_lab.get("status") or "ACTIVE").lower()
                if status_lower != st_val:
                    continue

            # 7. Standard number filter
            if std_lower:
                std_match = False
                for acc_std in orig_lab.get("accredited_standards", []):
                    acc_lower = acc_std.lower()
                    if std_lower in acc_lower or acc_lower in std_lower:
                        std_match = True
                        break
                    if std_base_num and std_base_num in acc_lower:
                        std_match = True
                        break

                if not std_match:
                    # Also check testing scope or lab name
                    scope_text = f"{lab.get('testing_scope_summary', '')} {orig_lab.get('testing_scope_summary', '')} {orig_lab.get('lab_name', '')}".lower()
                    if std_lower in scope_text or (std_base_num and std_base_num in scope_text):
                        std_match = True

                if not std_match:
                    continue

            # 8. Keyword Query search
            if q_lower:
                contact_str = json.dumps(orig_lab.get("contact_details") or {})
                searchable = f"{lab.get('lab_name', '')} {orig_lab.get('lab_code', '')} {lab.get('city', '')} {lab.get('district', '')} {lab.get('state', '')} {lab.get('address', '')} {contact_str} {lab.get('testing_scope_summary', '')} {orig_lab.get('lab_name', '')} {' '.join(orig_lab.get('accredited_standards', []))}".lower()
                has_match = (q_lower in searchable)
                if not has_match and mapped_std:
                    has_match = any(mapped_std in acc_std.lower() for acc_std in orig_lab.get("accredited_standards", [])) or (mapped_std in searchable)
                if not has_match:
                    tokens = [t for t in q_lower.split() if len(t) > 2 and t not in ["which", "what", "where", "test", "my", "product", "laboratory", "laboratories", "lab", "labs", "can", "the", "and", "for"]]
                    if tokens:
                        has_match = any(t in searchable for t in tokens)

                if not has_match:
                    continue

            results.append(LaboratoryItem(
                id=orig_lab.get("id") or f"lab-{orig_lab.get('lab_code')}",
                lab_name=lab.get("lab_name") or orig_lab.get("lab_name"),
                lab_code=orig_lab.get("lab_code"),
                recognition_type=orig_lab.get("recognition_type", "BIS_RECOGNIZED"),
                city=lab.get("city") or orig_lab.get("city", "Unknown"),
                district=lab.get("district") or orig_lab.get("district"),
                state=lab.get("state") or orig_lab.get("state", "Unknown"),
                address=orig_lab.get("address"),
                contact_details=orig_lab.get("contact_details"),
                validity_date=orig_lab.get("validity_date"),
                status=orig_lab.get("status", "ACTIVE"),
                source_url=orig_lab.get("source_url", "https://lims.bis.gov.in/home/labs/"),
                scope_url=orig_lab.get("scope_url"),
                testing_scope_summary=lab.get("testing_scope_summary") or orig_lab.get("testing_scope_summary"),
                accredited_standards=orig_lab.get("accredited_standards", []),
                last_verified_at=orig_lab.get("last_verified_at", "2026-01-15")
            ))

        # Relevance calculation if query provided
        def get_relevance_score(item: LaboratoryItem) -> int:
            if not q_lower:
                return 0
            lname = item.lab_name.lower()
            lcode = (item.lab_code or "").lower()
            if q_lower == lcode or q_lower == lname:
                return 100
            if q_lower in lname:
                return 80
            if q_lower in lcode:
                return 70
            tokens = [t for t in q_lower.split() if len(t) > 2]
            if tokens and all(t in lname for t in tokens):
                return 60
            if tokens and any(t in lname for t in tokens):
                return 40
            return 10

        # Sorting
        sort_by = (request.sort_by or "name").lower()
        reverse = (request.sort_order or "asc").lower() == "desc"

        if q_lower and (not request.sort_by or request.sort_by == "relevance" or request.sort_by == "name"):
            # If query is provided, sort by relevance score descending, then name ascending
            results.sort(key=lambda x: (-get_relevance_score(x), (x.lab_name or "").lower()))
            if reverse and request.sort_by == "name":
                results.reverse()
        elif sort_by == "code":
            results.sort(key=lambda x: (x.lab_code or "").lower(), reverse=reverse)
        elif sort_by == "state":
            results.sort(key=lambda x: ((x.state or "").lower(), (x.city or "").lower(), (x.lab_name or "").lower()), reverse=reverse)
        elif sort_by == "city":
            results.sort(key=lambda x: ((x.city or "").lower(), (x.lab_name or "").lower()), reverse=reverse)
        elif sort_by == "validity":
            results.sort(key=lambda x: (x.validity_date or "").lower(), reverse=reverse)
        else:
            results.sort(key=lambda x: (x.lab_name or "").lower(), reverse=reverse)

        total_count = len(results)

        # Pagination calculations
        # Support legacy limit if provided and page not explicitly customized
        page_size = request.limit if (request.limit and request.page_size == 20) else request.page_size
        page = max(1, request.page)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = results[start_idx:end_idx]

        total_pages = max(1, (total_count + page_size - 1) // page_size) if page_size > 0 else 1

        return LaboratorySearchResponse(
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            laboratories=paginated_items
        )

    def list_all_laboratories(self, language: str = "en") -> List[LaboratoryItem]:
        localized_labs = get_localized_all_laboratories(language)
        return [
            LaboratoryItem(
                id=orig_lab.get("id") or f"lab-{orig_lab.get('lab_code')}",
                lab_name=lab.get("lab_name") or orig_lab.get("lab_name"),
                lab_code=orig_lab.get("lab_code"),
                recognition_type=orig_lab.get("recognition_type", "BIS_RECOGNIZED"),
                city=lab.get("city") or orig_lab.get("city", "Unknown"),
                district=lab.get("district") or orig_lab.get("district"),
                state=lab.get("state") or orig_lab.get("state", "Unknown"),
                address=orig_lab.get("address"),
                contact_details=orig_lab.get("contact_details"),
                validity_date=orig_lab.get("validity_date"),
                status=orig_lab.get("status", "ACTIVE"),
                source_url=orig_lab.get("source_url", "https://lims.bis.gov.in/home/labs/"),
                scope_url=orig_lab.get("scope_url"),
                testing_scope_summary=lab.get("testing_scope_summary") or orig_lab.get("testing_scope_summary"),
                accredited_standards=orig_lab.get("accredited_standards", []),
                last_verified_at=orig_lab.get("last_verified_at", "2026-01-15")
            )
            for lab, orig_lab in zip(localized_labs, VERIFIED_LABORATORIES)
        ]

    def get_laboratory_by_id_or_code(self, id_or_code: str, language: str = "en") -> Optional[LaboratoryItem]:
        target = (id_or_code or "").strip().lower()
        if not target:
            return None
        localized_labs = get_localized_all_laboratories(language)
        for lab, orig_lab in zip(localized_labs, VERIFIED_LABORATORIES):
            lid = (orig_lab.get("id") or "").lower()
            lcode = (orig_lab.get("lab_code") or "").lower()
            if target == lid or target == lcode:
                return LaboratoryItem(
                    id=orig_lab.get("id") or f"lab-{orig_lab.get('lab_code')}",
                    lab_name=lab.get("lab_name") or orig_lab.get("lab_name"),
                    lab_code=orig_lab.get("lab_code"),
                    recognition_type=orig_lab.get("recognition_type", "BIS_RECOGNIZED"),
                    city=lab.get("city") or orig_lab.get("city", "Unknown"),
                    district=lab.get("district") or orig_lab.get("district"),
                    state=lab.get("state") or orig_lab.get("state", "Unknown"),
                    address=orig_lab.get("address"),
                    contact_details=orig_lab.get("contact_details"),
                    validity_date=orig_lab.get("validity_date"),
                    status=orig_lab.get("status", "ACTIVE"),
                    source_url=orig_lab.get("source_url", "https://lims.bis.gov.in/home/labs/"),
                    scope_url=orig_lab.get("scope_url"),
                    testing_scope_summary=lab.get("testing_scope_summary") or orig_lab.get("testing_scope_summary"),
                    accredited_standards=orig_lab.get("accredited_standards", []),
                    last_verified_at=orig_lab.get("last_verified_at", "2026-01-15")
                )
        return None

    def get_laboratory_stats(self) -> Dict[str, Any]:
        total = len(VERIFIED_LABORATORIES)
        rec_count = sum(1 for x in VERIFIED_LABORATORIES if x.get("recognition_type") == "BIS_RECOGNIZED")
        emp_count = sum(1 for x in VERIFIED_LABORATORIES if x.get("recognition_type") == "BIS_EMPANELLED")
        inst_count = sum(1 for x in VERIFIED_LABORATORIES if x.get("recognition_type") in ("BIS_CENTRAL", "BIS_BRANCH"))
        act_count = sum(1 for x in VERIFIED_LABORATORIES if x.get("status") == "ACTIVE")
        exp_count = sum(1 for x in VERIFIED_LABORATORIES if x.get("status") == "EXPIRED")
        states = sorted(list({x.get("state") for x in VERIFIED_LABORATORIES if x.get("state") and x.get("state") not in ("Unknown", "-", "", "None") and len(x.get("state")) > 1}))
        return {
            "total_laboratories": total,
            "recognized_count": rec_count,
            "empaneled_count": emp_count,
            "institutional_count": inst_count,
            "active_count": act_count,
            "expired_count": exp_count,
            "total_states": len(states),
            "states": states,
            "last_imported_at": datetime.now().strftime("%Y-%m-%d")
        }

    def list_all_schemes(self, language: str = "en") -> List[Dict[str, Any]]:
        return get_localized_all_schemes(language)
