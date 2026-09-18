from typing import List, Optional
from app.schemas.intelligence import (
    LaboratorySearchRequest,
    LaboratorySearchResponse,
    LaboratoryItem
)
from app.db.seed_intelligence import (
    VERIFIED_LABORATORIES,
    get_localized_all_laboratories,
    get_localized_laboratory
)


class LaboratoryService:
    """
    Structured laboratory guidance and search service.
    Filters verified BIS-recognized and NABL-accredited laboratories by state, city,
    standard number, and testing scope with multilingual localization.
    """

    def search_laboratories(self, request: LaboratorySearchRequest) -> LaboratorySearchResponse:
        results: List[LaboratoryItem] = []

        q_lower = (request.query or "").strip().lower()
        city_lower = (request.city or "").strip().lower()
        state_lower = (request.state or "").strip().lower()
        std_lower = (request.standard_number or "").strip().lower()
        recog_lower = (request.recognition_type or "").strip().lower()
        lang = request.language or "en"

        localized_labs = get_localized_all_laboratories(lang)

        for lab, orig_lab in zip(localized_labs, VERIFIED_LABORATORIES):
            # Filter by City
            if city_lower:
                if city_lower not in orig_lab["city"].lower() and city_lower not in lab["city"].lower():
                    continue

            # Filter by State
            if state_lower:
                if state_lower not in orig_lab["state"].lower() and state_lower not in lab["state"].lower():
                    continue

            # Filter by Recognition Type
            if recog_lower and recog_lower not in orig_lab["recognition_type"].lower():
                continue

            # Filter by Standard Number
            if std_lower:
                std_match = any(std_lower in acc_std.lower() for acc_std in orig_lab["accredited_standards"])
                if not std_match:
                    continue

            # Filter by general keyword query (lab name, testing scope, address)
            if q_lower:
                searchable = f"{lab['lab_name']} {lab['city']} {lab['state']} {lab.get('testing_scope_summary', '')} {orig_lab['lab_name']} {orig_lab['state']} {' '.join(orig_lab['accredited_standards'])}".lower()
                if q_lower not in searchable:
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

    def list_all(self, language: str = "en") -> List[LaboratoryItem]:
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
