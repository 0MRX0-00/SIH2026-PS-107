from typing import List, Optional
from app.schemas.intelligence import (
    StandardListItem,
    StandardDetailResponse,
    StandardSectionItem
)
from app.db.seed_intelligence import (
    VERIFIED_STANDARDS,
    get_localized_standard,
    get_localized_all_standards
)


class StandardsService:
    """
    Standards Explorer and Standard Details service.
    Provides structured querying for Indian Standards, division filtering, clause navigation,
    and QCO status inspection with multilingual localization.
    """

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

        # Retrieve standards localized to target language
        localized_list = get_localized_all_standards(language)

        for std, orig_std in zip(localized_list, VERIFIED_STANDARDS):
            # Check division against both localized and original division
            if division:
                if div_lower not in orig_std["division"].lower() and div_lower not in std["division"].lower():
                    continue

            if qco_only is not None and orig_std["is_qco_mandatory"] != qco_only:
                continue

            if q_lower:
                searchable = f"{std['standard_number']} {std['title']} {std['division']} {std.get('scope_summary', '')} {orig_std['title']} {orig_std['division']}".lower()
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

    def get_standard_details(self, standard_id_or_number: str, language: str = "en") -> Optional[StandardDetailResponse]:
        lookup = standard_id_or_number.strip().lower()

        matched_idx = next(
            (
                idx for idx, s in enumerate(VERIFIED_STANDARDS)
                if s["id"].lower() == lookup
                or lookup in s["standard_number"].lower()
                or s["standard_number"].lower() == lookup
                or lookup in s["standard_number"].replace(" ", "").lower()
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
