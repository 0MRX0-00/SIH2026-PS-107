"""
BIS Product Certification Guidance Centre Service.
Generates structured, verifiable guidance for BIS product certification pathways
covering Scheme-I (ISI Mark), Scheme-II (CRS), Scheme-IV (FMCS), Scheme-X (Capital Goods),
and Hallmarking with multilingual support (English, Hindi, Tamil).
"""
from typing import Optional, List, Dict, Any
from app.schemas.intelligence import (
    CertificationRoadmapRequest,
    CertificationRoadmapResponse,
    RoadmapStepItem,
    DocumentChecklistItem,
    OfficialSourceCard
)
from app.schemas.chat import SourceItem as CitationItem
from app.db.seed_intelligence import VERIFIED_STANDARDS, VERIFIED_SCHEMES


class CertificationNavigatorService:
    """
    BIS Product Certification Guidance Navigator Service.
    Determines potentially relevant certification routes, step-by-step compliance workflows,
    categorized document checklists, clarifying questions, and verified official BIS source links.
    """

    OFFICIAL_BIS_SOURCES = [
        {
            "title": "Products under Compulsory Certification",
            "url": "https://www.bis.gov.in/product-certification/products-under-compulsory-certification/?lang=en",
            "description": "Official gazetted list of products and Indian Standards under mandatory Quality Control Orders (QCOs).",
            "category": "MANDATORY_QCO_REGISTRY",
            "verification_date": "Current Official Gazette",
            "is_official_portal": True
        },
        {
            "title": "Product Certification Process (Scheme-I)",
            "url": "https://www.bis.gov.in/product-certification/product-certification-process/?lang=en",
            "description": "Standard operating procedures, factory audit norms, and sample testing guidelines under Scheme-I.",
            "category": "CERTIFICATION_PROCESS",
            "verification_date": "BIS Conformity Regulations 2018",
            "is_official_portal": True
        },
        {
            "title": "Product-Specific Guidelines",
            "url": "https://www.bis.gov.in/product-certification/product-specific-information-2/?lang=en",
            "description": "Standard-specific guidelines for Indian Standards, Scheme of Inspection & Testing (SIT), and raw material norms.",
            "category": "PRODUCT_SPECIFIC_SIT",
            "verification_date": "Updated per Standard Revision",
            "is_official_portal": True
        },
        {
            "title": "BIS Fee Information & Cost Schedule",
            "url": "https://www.bis.gov.in/product-certification/product-certification-fee/?lang=en",
            "description": "Prescribed application fees, assessment charges, laboratory testing rates, and annual marking fees.",
            "category": "FEE_STRUCTURE",
            "verification_date": "Official BIS Fee Schedule",
            "is_official_portal": True
        },
        {
            "title": "ManakOnline Single-Window Portal",
            "url": "https://www.manakonline.in/",
            "description": "Official Government of India portal for e-filing of BIS Scheme-I, CRS, and FMCS applications.",
            "category": "OFFICIAL_PORTAL",
            "verification_date": "Active Portal",
            "is_official_portal": True
        }
    ]

    OFFICIAL_SOURCES_TRANSLATIONS = {
        "hi": {
            "Products under Compulsory Certification": {
                "title": "अनिवार्य प्रमाणन के अंतर्गत उत्पाद",
                "description": "अनिवार्य गुणवत्ता नियंत्रण आदेशों (QCO) के तहत उत्पादों और भारतीय मानकों की आधिकारिक राजपत्रित सूची।",
                "verification_date": "वर्तमान आधिकारिक राजपत्र"
            },
            "Product Certification Process (Scheme-I)": {
                "title": "उत्पाद प्रमाणन प्रक्रिया (योजना-I)",
                "description": "योजना-I के तहत मानक संचालन प्रक्रियाएं, कारखाना लेखापरीक्षा मानदंड और नमूना परीक्षण दिशानिर्देश।",
                "verification_date": "बीआईएस अनुरूपता विनियम 2018"
            },
            "Product-Specific Guidelines": {
                "title": "उत्पाद-विशिष्ट दिशानिर्देश",
                "description": "भारतीय मानकों, निरीक्षण एवं परीक्षण योजना (SIT) और कच्चे माल के मानदंडों के लिए उत्पाद-विशिष्ट दिशानिर्देश।",
                "verification_date": "मानक संशोधन के अनुसार अद्यतन"
            },
            "BIS Fee Information & Cost Schedule": {
                "title": "बीआईएस शुल्क जानकारी एवं लागत अनुसूची",
                "description": "निर्धारित आवेदन शुल्क, मूल्यांकन शुल्क, प्रयोगशाला परीक्षण दरें और वार्षिक अंकन शुल्क।",
                "verification_date": "आधिकारिक बीआईएस शुल्क अनुसूची"
            },
            "ManakOnline Single-Window Portal": {
                "title": "मानकऑनलाइन सिंगल-विंडो पोर्टल",
                "description": "बीआईएस योजना-I, सीआरएस और एफएमसीएस आवेदनों के ई-फाइलिंग के लिए भारत सरकार का आधिकारिक पोर्टल।",
                "verification_date": "सक्रिय पोर्टल"
            }
        },
        "ta": {
            "Products under Compulsory Certification": {
                "title": "கட்டாய சான்றிதழின் கீழ் உள்ள பொருட்கள்",
                "description": "கட்டாய தரக் கட்டுப்பாட்டு ஆணைகளின் (QCOs) கீழ் உள்ள பொருட்கள் மற்றும் இந்திய தரநிலைகளின் அதிகாரப்பூர்வ அரசிதழ் பட்டியல்.",
                "verification_date": "தற்போதைய அதிகாரப்பூர்வ அரசிதழ்"
            },
            "Product Certification Process (Scheme-I)": {
                "title": "தயாரிப்பு சான்றிதழ் செயல்முறை (திட்டம்-I)",
                "description": "திட்டம்-I இன் கீழ் நிலையான செயல்பாட்டு நடைமுறைகள், தொழிற்சாலை தணிக்கை விதிமுறைகள் மற்றும் மாதிரி சோதனை வழிகாட்டுதல்கள்.",
                "verification_date": "BIS இணக்க விதிமுறைகள் 2018"
            },
            "Product-Specific Guidelines": {
                "title": "தயாரிப்பு சார்ந்த வழிகாட்டுதல்கள்",
                "description": "இந்திய தரநிலைகள், ஆய்வு & சோதனைத் திட்டம் (SIT) மற்றும் மூலப்பொருள் விதிமுறைகளுக்கான தயாரிப்பு சார்ந்த வழிகாட்டுதல்கள்.",
                "verification_date": "தரநிலை திருத்தத்தின்படி புதுப்பிக்கப்பட்டது"
            },
            "BIS Fee Information & Cost Schedule": {
                "title": "BIS கட்டண தகவல் & செலவு அட்டவணை",
                "description": "விதிக்கப்பட்ட விண்ணப்பக் கட்டணம், மதிப்பீட்டுக் கட்டணங்கள், ஆய்வக சோதனைக் கட்டணங்கள் மற்றும் வருடாந்திர முத்திரைக் கட்டணங்கள்.",
                "verification_date": "அதிகாரப்பூர்வ BIS கட்டண அட்டவணை"
            },
            "ManakOnline Single-Window Portal": {
                "title": "மானக்ஆன்லைன் ஒற்றைச் சாளர போர்டல்",
                "description": "BIS திட்டம்-I, CRS மற்றும் FMCS விண்ணப்பங்களை மின்-தாக்கல் செய்வதற்கான இந்திய அரசின் அதிகாரப்பூர்வ போர்டல்.",
                "verification_date": "செயலில் உள்ள போர்டல்"
            }
        }
    }

    def generate_roadmap(self, request: CertificationRoadmapRequest) -> CertificationRoadmapResponse:
        product_name = (request.product_name or "").strip()
        product_category = (request.product_category or "").strip()
        intended_use = (request.intended_use or "").strip()
        country_of_manufacture = (request.country_of_manufacture or "India").strip()
        manufacturer_type = (request.manufacturer_type or "DOMESTIC_MANUFACTURER").strip()
        product_description = (request.product_description or "").strip()
        std_query = (request.standard_number or "").strip()
        scheme_query = (request.scheme_code or "").strip()
        lang = (request.language or "en").lower()

        # Combine text for matching
        search_corpus = f"{product_name} {product_category} {intended_use} {product_description}".lower()

        # 1. Resolve Standard Match
        matched_std: Optional[Dict[str, Any]] = None
        evidence_level = "PRELIMINARY_GENERAL_GUIDANCE"

        if std_query:
            matched_std = next(
                (s for s in VERIFIED_STANDARDS if std_query.lower() in s["standard_number"].lower()),
                None
            )
            if matched_std:
                evidence_level = "VERIFIED_STANDARD_MATCH"
        elif search_corpus.strip():
            # Match keywords
            for s in VERIFIED_STANDARDS:
                std_text = f"{s['standard_number']} {s['title']} {s.get('scope_summary', '')}".lower()
                # Check for direct word matches of significant length
                words = [w for w in search_corpus.split() if len(w) > 3]
                if any(w in std_text for w in words):
                    matched_std = s
                    evidence_level = "VERIFIED_STANDARD_MATCH"
                    break

        # 2. Determine Certification Scheme
        is_foreign = (
            country_of_manufacture.lower() not in ["india", "in", "domestic", ""] or
            manufacturer_type in ["FOREIGN_MANUFACTURER", "AUTHORIZED_INDIAN_REPRESENTATIVE"]
        )

        matched_scheme: Optional[Dict[str, Any]] = None

        if scheme_query:
            q = scheme_query.lower().strip()
            matched_scheme = next(
                (
                    sc for sc in VERIFIED_SCHEMES 
                    if q == sc["scheme_code"].lower() 
                    or any(q == a.lower() for a in sc.get("legacy_aliases", []))
                    or q in sc["scheme_code"].lower()
                    or any(q in a.lower() for a in sc.get("legacy_aliases", []))
                    or q in sc["name"].lower()
                ),
                None
            )

        if not matched_scheme:
            # Check management systems
            is_management_system = any(k in search_corpus for k in [
                "iso 9001", "iso 14001", "iso 22000", "iso 45001", "iso 50001", "iso 27001", "iso 13485", "management system", "qms", "ems", "fsms"
            ]) or (product_category.lower() in ["management systems", "qms", "services"])

            # Check laboratory recognition
            is_lab_recognition = any(k in search_corpus for k in [
                "laboratory recognition", "lims", "testing laboratory", "lab recognition", "empanelment"
            ])

            # Check eco mark
            is_eco_mark = any(k in search_corpus for k in [
                "eco mark", "ecomark", "environment-friendly", "eco friendly", "green mark"
            ])

            # Check batch / lot CoC
            is_coc = any(k in search_corpus for k in [
                "certificate of conformity", "scheme iii", "batch certification", "lot certification", "consignment"
            ])

            # Evaluate product characteristics
            is_it_electronics = any(k in search_corpus for k in [
                "laptop", "mobile", "charger", "adapter", "battery", "lithium", "smart watch", "server", "electronics", "it goods", "led", "solar pv"
            ]) or (matched_std and ("information technology" in matched_std.get("division", "").lower() or "13252" in matched_std["standard_number"] or "16046" in matched_std["standard_number"]))

            is_capital_goods = any(k in search_corpus for k in [
                "machinery", "machine", "heavy equipment", "compressor", "transformer", "plant", "capital goods", "industrial crane", "pump"
            ]) or (product_category.lower() in ["capital goods", "machinery", "heavy electrical"])

            is_precious_metals = any(k in search_corpus for k in [
                "gold", "silver", "jewellery", "jewelry", "bullion", "hallmark", "huid"
            ]) or (product_category.lower() in ["precious metals", "jewellery", "gold", "silver"])

            if is_management_system:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_IV_MSCS"), None)
            elif is_lab_recognition:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "LABORATORY_RECOGNITION"), None)
            elif is_eco_mark:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "ECO_MARK"), None)
            elif is_coc:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_III_COC"), None)
            elif is_precious_metals:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "HALLMARKING"), None)
            elif is_it_electronics:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_II_CRS"), None)
            elif is_capital_goods and not is_foreign:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_X_CAPITAL_GOODS"), None)
            elif is_foreign:
                # Foreign non-CRS products go through FMCS under Scheme-I
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_I_FMCS"), None)
            else:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_I_ISI_NORMAL"), None)

        if not matched_scheme:
            matched_scheme = VERIFIED_SCHEMES[0]


        # 3. Product & Standard Metadata
        product_display = product_name or (matched_std["title"] if matched_std else "Specified Product")
        std_number = matched_std["standard_number"] if matched_std else (std_query or None)
        is_qco = matched_std["is_qco_mandatory"] if matched_std else False
        qco_order = matched_std.get("qco_order_number") if matched_std else None
        requires_air = is_foreign or matched_scheme.get("scheme_code") in ("SCHEME_I_FMCS", "SCHEME_IV_FMCS") or matched_scheme.get("manufacturer_scope") == "FOREIGN"



        # 4. Citations
        citations: List[CitationItem] = []
        if matched_std:
            citations.append(CitationItem(
                id=1,
                standard_number=matched_std["standard_number"],
                title=matched_std["title"],
                clause="1.1 Scope & Applicability",
                page=1,
                snippet=matched_std.get("scope_summary", matched_std["title"])[:250],
                source="BIS Official Standard"
            ))
            if is_qco and qco_order:
                citations.append(CitationItem(
                    id=2,
                    standard_number=matched_std["standard_number"],
                    title=f"Quality Control Order: {qco_order}",
                    clause="Section 16, BIS Act 2016",
                    page=1,
                    snippet=f"Mandatory certification enforced under {qco_order}. Prohibits manufacture, import, sale without standard mark.",
                    source="Ministry Gazette Notification"
                ))

        # 5. Clarifying Questions Generation
        clarifying_questions: List[str] = []
        if not std_number:
            if lang == "hi":
                clarifying_questions.append("क्या आपने अपने उत्पाद के लिए विशिष्ट भारतीय मानक (IS नंबर) की पुष्टि की है? (जैसे IS 1293 या IS 13252)")
                clarifying_questions.append("उत्पाद के मुख्य तकनीकी विनिर्देश (रेटेड वोल्टेज, शक्ति, सामग्री संरचना) क्या हैं?")
            elif lang == "ta":
                clarifying_questions.append("உங்கள் தயாரிப்புக்கான குறிப்பிட்ட இந்திய தரநிலையை (IS எண்) உறுதிப்படுத்தியுள்ளீர்களா?")
                clarifying_questions.append("தயாரிப்பின் முக்கிய தொழில்நுட்ப விவரக்குறிப்புகள் (மின்னழுத்தம், திறன், மூலப்பொருள்) என்ன?")
            else:
                clarifying_questions.append("Have you identified the exact Indian Standard (IS number) applicable to your specific product model and voltage rating?")
                clarifying_questions.append("What are the key technical specifications (e.g. rated voltage/wattage, material composition, domestic vs. commercial grade)?")

        if not intended_use:
            if lang == "hi":
                clarifying_questions.append("क्या यह उत्पाद घरेलू (Household), वाणिज्यिक (Commercial) या औद्योगिक (Industrial) उपयोग के लिए है?")
            elif lang == "ta":
                clarifying_questions.append("இந்த தயாரிப்பு வீட்டு உபயோகத்திற்கா, வணிக பயன்பாட்டிற்கா அல்லது தொழில்துறை பயன்பாட்டிற்கா?")
            else:
                clarifying_questions.append("Is the intended use strictly domestic/household, commercial, medical, or heavy industrial?")

        if is_foreign and not manufacturer_type:
            if lang == "hi":
                clarifying_questions.append("क्या आपने भारत में एक कानूनी रूप से अधिकृत भारतीय प्रतिनिधि (AIR) नियुक्त किया है?")
            elif lang == "ta":
                clarifying_questions.append("இந்தியாவில் சட்டப்பூர்வமாக அங்கீகரிக்கப்பட்ட இந்திய பிரதிநிதியை (AIR) நியமித்துள்ளீர்களா?")
            else:
                clarifying_questions.append("Have you appointed a legally registered Authorized Indian Representative (AIR) residing in India to represent the foreign manufacturing unit?")

        # 6. Route Rationale
        route_rationale = self._build_route_rationale(
            scheme_code=matched_scheme["scheme_code"],
            product_display=product_display,
            std_number=std_number,
            is_qco=is_qco,
            is_foreign=is_foreign,
            country=country_of_manufacture,
            lang=lang
        )

        # 7. Step-by-Step 6-Stage Compliance Guide
        steps = self._build_steps(
            scheme=matched_scheme,
            product_display=product_display,
            std_number=std_number,
            is_qco=is_qco,
            qco_order=qco_order,
            is_foreign=is_foreign,
            citations=citations,
            lang=lang
        )

        # 8. Dynamic Categorized Document Checklist
        document_checklist = self._build_document_checklist(
            scheme_code=matched_scheme["scheme_code"],
            is_foreign=is_foreign,
            has_standard=matched_std is not None,
            lang=lang
        )

        # 9. Official Source Cards
        official_sources = []
        for s in self.OFFICIAL_BIS_SOURCES:
            src_title = s["title"]
            src_desc = s["description"]
            src_date = s.get("verification_date")
            if lang in ("hi", "ta") and s["title"] in self.OFFICIAL_SOURCES_TRANSLATIONS.get(lang, {}):
                t_card = self.OFFICIAL_SOURCES_TRANSLATIONS[lang][s["title"]]
                src_title = t_card.get("title", src_title)
                src_desc = t_card.get("description", src_desc)
                src_date = t_card.get("verification_date", src_date)

            official_sources.append(
                OfficialSourceCard(
                    title=src_title,
                    url=s["url"],
                    description=src_desc,
                    category=s["category"],
                    verification_date=src_date,
                    is_official_portal=s.get("is_official_portal", True)
                )
            )

        # 10. Localized Disclaimer
        if lang == "hi":
            disclaimer_text = (
                "आधिकारिक अस्वीकरण: यह मार्गदर्शन उपलब्ध बीआईएस और मंत्रालय की अधिसूचनाओं से तैयार किया गया एक तकनीकी सहायता उपकरण है। "
                "यह आधिकारिक बीआईएस अनुमोदन या प्रमाणन का कानूनी अनुदान नहीं है। अंतिम प्रयोज्यता की पुष्टि संबंधित भारतीय मानक, गुणवत्ता नियंत्रण आदेश (QCO) और आधिकारिक बीआईएस अधिसूचनाओं से की जानी चाहिए।"
            )
            scheme_name_display = matched_scheme.get("name", "योजना-I: उत्पाद प्रमाणन (ISI मार्क)")
        elif lang == "ta":
            disclaimer_text = (
                "அதிகாரப்பூர்வ மறுப்பு: இந்த வழிகாட்டுதல் கிடைக்கக்கூடிய BIS மற்றும் அமைச்சக அறிவிப்புகளிலிருந்து உருவாக்கப்பட்ட தொழில்நுட்ப உதவி கருவியாகும். "
                "இது அதிகாரப்பூர்வ BIS ஒப்புதல் அல்லது சட்டப்பூர்வ சான்றிதழ் அல்ல. இறுதி பொருந்தக்கூடிய தன்மையை தொடர்புடைய இந்திய தரநிலை, தரக் கட்டுப்பாட்டு ஆணை (QCO) மற்றும் அதிகாரப்பூர்வ BIS அறிவிப்புகள் மூலம் உறுதிப்படுத்த வேண்டும்."
            )
            scheme_name_display = matched_scheme.get("name", "திட்டம்-I: தயாரிப்பு சான்றிதழ் (ISI முத்திரை)")
        else:
            disclaimer_text = (
                "Official Disclaimer: This guidance is an informative technical navigation tool generated from available BIS and ministry notifications. "
                "It does not constitute official BIS approval or legal grant of certification. Final applicability must be confirmed with the relevant Indian Standard, Quality Control Order (QCO), and official BIS notifications."
            )
            scheme_name_display = matched_scheme.get("name", "Scheme-I: Product Certification (ISI Mark)")

        return CertificationRoadmapResponse(
            product=product_display,
            product_category=product_category or None,
            intended_use=intended_use or None,
            country_of_manufacture=country_of_manufacture,
            manufacturer_type=manufacturer_type,
            standard_number=std_number,
            applicable_scheme=matched_scheme.get("scheme_code", "SCHEME_I_ISI_NORMAL"),
            scheme_name=scheme_name_display,
            route_rationale=route_rationale,
            is_mandatory_qco=is_qco,
            qco_order_number=qco_order,
            evidence_level=evidence_level,
            requires_air=requires_air,
            clarifying_questions=clarifying_questions,
            steps=steps,
            document_checklist=document_checklist,
            official_sources=official_sources,
            disclaimer=disclaimer_text,
            citations=citations
        )

    def _build_route_rationale(
        self,
        scheme_code: str,
        product_display: str,
        std_number: Optional[str],
        is_qco: bool,
        is_foreign: bool,
        country: str,
        lang: str
    ) -> str:
        if lang == "hi":
            base = f"{product_display} के लिए बीआईएस प्रमाणन मार्ग कई प्रमुख कारकों पर निर्भर करता है: लागू भारतीय मानक, संबंधित मंत्रालय का गुणवत्ता नियंत्रण आदेश (QCO), निर्माण का देश और निर्माता का विधिक स्वरूप। "
            if is_foreign or scheme_code in ("SCHEME_I_FMCS", "SCHEME_IV_FMCS"):
                return base + f"चूंकि विनिर्माण स्थान भारत के बाहर ({country}) है और यह गैर-सीआरएस उत्पाद है, इसलिए यह 'विदेशी निर्माता प्रमाणन योजना (Scheme-I FMCS)' के अंतर्गत आता है (सांविधिक रूप से बीआईएस अनुरूपता मूल्यांकन विनियम 2018 के तहत योजना-I में शासित)। इसके लिए एक अधिकृत भारतीय प्रतिनिधि (AIR), बीआईएस अधिकारी द्वारा ऑन-साइट ऑडिट, नमूना परीक्षण और USD 10,000 बैंक गारंटी अनिवार्य है।"
            elif scheme_code == "SCHEME_I_ISI_SIMPLIFIED":
                return base + "घरेलू निर्माताओं के लिए 'योजना-I सरलीकृत प्रक्रिया (Fast-Track ISI Mark)' लागू होती है, जो बीआईएस मान्यता प्राप्त प्रयोगशाला की पूर्ण परीक्षण रिपोर्ट और SIT अनुपालन के आधार पर 30 दिनों के भीतर त्वरित लाइसेंस प्रदान करती है।"
            elif scheme_code == "ECO_MARK":
                return base + "पर्यावरण-अनुकूल उत्पादों के लिए 'इको मार्क योजना' लागू होती है, जिसमें उत्पाद को मानक ISI गुणवत्ता के साथ-साथ MoEFCC के विशिष्ट पर्यावरणीय मानदंडों को पूरा करना होता है।"
            elif scheme_code == "SCHEME_II_CRS":
                return base + "इलेक्ट्रॉनिक्स, आईटी सामान और सौर पीवी के लिए 'अनिवार्य पंजीकरण योजना (Scheme-II CRS)' लागू होती है, जिसमें बीआईएस मान्यता प्राप्त लैब से परीक्षण रिपोर्ट के आधार पर बिना फैक्ट्री ऑडिट के स्व-घोषणा पंजीकरण (R-XXXXXXXX) दिया जाता है।"
            elif scheme_code == "SCHEME_III_COC":
                return base + "विशिष्ट बैचों, आयातित खेपों या कस्टम ऑर्डरों के लिए 'योजना-III अनुरूपता प्रमाण पत्र (CoC)' लागू होती है, जो सांख्यिकीय नमूनाकरण और लैब परीक्षण के बाद निर्धारित खेप मात्रा के लिए प्रमाण पत्र जारी करती है।"
            elif scheme_code == "SCHEME_IV_MSCS":
                return base + "संगठनात्मक प्रबंधन प्रणालियों (ISO 9001 QMS, ISO 14001 EMS, ISO 22000 FSMS आदि) के लिए 'योजना-IV प्रबंधन प्रणाली प्रमाणन योजना (MSCS)' लागू होती है।"
            elif scheme_code == "SCHEME_X_CAPITAL_GOODS":
                return base + "भारी मशीनरी और पूंजीगत उपकरणों के लिए 'योजना-X (Scheme-X)' लागू होती है, जो तकनीकी निर्माण फाइल (TCF) और इन-सीटू परीक्षण पर आधारित सरलीकृत प्रमाणन प्रक्रिया प्रदान करती है।"
            elif scheme_code == "HALLMARKING":
                return base + "स्वर्ण और रजत आभूषणों के लिए 'हॉलमार्किंग योजना' लागू है, जिसके तहत मान्यता प्राप्त AHC केंद्रों से 6-अंकीय HUID लेजर अंकन अनिवार्य है।"
            elif scheme_code == "LABORATORY_RECOGNITION":
                return base + "परीक्षण प्रयोगशालाओं के लिए 'प्रयोगशाला मान्यता योजना (LRS / LIMS)' लागू होती है, जो NABL प्रत्यायन के आधार पर बीआईएस सांविधिक परीक्षण हेतु पैनलबद्धता प्रदान करती है।"
            else:
                return base + f"सामान्य घरेलू और औद्योगिक उत्पादों के लिए 'योजना-I सामान्य प्रक्रिया (ISI मार्क)' लागू होती है जिसमें प्रारंभिक फैक्ट्री गुणवत्ता ऑडिट, इन-हाउस परीक्षण उपकरण और लैब अनुरूपता परीक्षण शामिल है।"
        elif lang == "ta":
            base = f"{product_display} க்கான BIS சான்றிதழ் வழி பல முக்கிய காரணிகளைப் பொறுத்தது: பொருந்தக்கூடிய இந்திய தரநிலை, சம்பந்தப்பட்ட அமைச்சகத்தின் தரக் கட்டுப்பாட்டு ஆணை (QCO), உற்பத்தி செய்யும் நாடு மற்றும் உற்பத்தியாளரின் சட்டப்பூர்வ நிலை. "
            if is_foreign or scheme_code in ("SCHEME_I_FMCS", "SCHEME_IV_FMCS"):
                return base + f"உற்பத்தி ஆலை இந்தியாவுக்கு வெளியே ({country}) அமைந்துள்ளதால், இது 'வெளிநாட்டு உற்பத்தியாளர்கள் சான்றிதழ் திட்டம் (Scheme-I FMCS)' இன் கீழ் வருகிறது (2018 விதிமுறைகளின்படி திட்டம்-I இன் கீழ் நிர்வகிக்கப்படுகிறது). இதற்கு அங்கீகரிக்கப்பட்ட இந்திய பிரதிநிதி (AIR) மற்றும் BIS அதிகாரியின் நேரடி வெளிநாட்டு ஆய்வு கட்டாயமாகும்."
            elif scheme_code == "SCHEME_I_ISI_SIMPLIFIED":
                return base + "உள்நாட்டு உற்பத்தியாளர்களுக்கு 'திட்டம்-I எளிமைப்படுத்தப்பட்ட நடைமுறை (விரைவு ISI முத்திரை)' பொருந்தும். இதில் அங்கீகரிக்கப்பட்ட ஆய்வக சோதனை அறிக்கை அடிப்படையில் 30 நாட்களுக்குள் விரைவு உரிமம் வழங்கப்படுகிறது."
            elif scheme_code == "ECO_MARK":
                return base + "சுற்றுச்சூழல் நட்பு தயாரிப்புகளுக்கு 'சுற்றுச்சூழல் முத்திரை திட்டம் (ECO Mark)' பொருந்தும். இதில் ISI தரநிலைகளுடன் சுற்றுச்சூழல் பாதுகாப்பு விதிகளும் சரிபார்க்கப்படுகின்றன."
            elif scheme_code == "SCHEME_II_CRS":
                return base + "மின்னணு மற்றும் தகவல் தொழில்நுட்ப சாதனங்களுக்கு 'கட்டாய பதிவுத் திட்டம் (Scheme-II CRS)' பொருந்தும். இதில் BIS ஆய்வக சோதனை அறிக்கை அடிப்படையில் சுய அறிவிப்பு பதிவு வழங்கப்படுகிறது."
            elif scheme_code == "SCHEME_III_COC":
                return base + "குறிப்பிட்ட சரக்கு தொகுதிகளுக்கு 'திட்டம்-III இணக்கச் சான்றிதழ் (CoC)' பொருந்தும். இதில் மாதிரி சோதனை அடிப்படையில் குறிப்பிட்ட தொகுதிக்கு சான்றிதழ் வழங்கப்படுகிறது."
            elif scheme_code == "SCHEME_IV_MSCS":
                return base + "மேலாண்மை அமைப்புகளுக்கு (ISO 9001, ISO 14001, ISO 22000) 'திட்டம்-IV மேலாண்மை அமைப்புகள் சான்றிதழ் திட்டம் (MSCS)' பொருந்தும்."
            elif scheme_code == "SCHEME_X_CAPITAL_GOODS":
                return base + "கனரக இயந்திரங்கள் மற்றும் தொழில்துறை உபகரணங்களுக்கு 'திட்டம்-X (Scheme-X)' பொருந்தும், இது தொழில்நுட்ப ஆவணக் கோப்பு மற்றும் நேரடி சோதனையை அடிப்படையாகக் கொண்டது."
            elif scheme_code == "HALLMARKING":
                return base + "தங்கம் மற்றும் வெள்ளி நகைகளுக்கு 'ஹால்மார்க்கிங் திட்டம்' பொருந்தும், இதில் AHC மையங்கள் மூலம் 6-இலக்க HUID குறியீடு கட்டாயமாகும்."
            elif scheme_code == "LABORATORY_RECOGNITION":
                return base + "சோதனை ஆய்வகங்களுக்கு 'ஆய்வக அங்கீகார திட்டம் (LRS / LIMS)' பொருந்தும்."
            else:
                return base + "பொதுவான உற்பத்தி பொருட்களுக்கு 'திட்டம்-I இயல்பான நடைமுறை (ISI முத்திரை)' பொருந்தும். இதில் தொழிற்சாலை தணிக்கை மற்றும் மாதிரி சோதனை ஆகியவை அடங்கும்."
        else:
            base = (
                f"The applicable BIS certification route for {product_display} depends on five critical parameters: "
                f"1) The applicable Indian Standard, 2) Relevant Quality Control Order (QCO) gazette status, "
                f"3) Country of manufacture, 4) Operational intended use, and 5) Legal status of the applicant. "
            )
            if is_foreign or scheme_code in ("SCHEME_I_FMCS", "SCHEME_IV_FMCS"):
                return base + (
                    f"Because manufacturing is located outside India ({country}) for a non-CRS product, the route is governed by "
                    f"Scheme-I: Foreign Manufacturers Certification Scheme (FMCS) under Schedule-I of the BIS (Conformity Assessment) Regulations, 2018. "
                    f"This route requires appointing an Authorized Indian Representative (AIR), submitting Form-V, facilitating an on-site physical factory audit "
                    f"by a BIS inspecting officer, air-freighting samples to an Indian laboratory, and furnishing a USD 10,000 Performance Bank Guarantee."
                )
            elif scheme_code == "SCHEME_I_ISI_SIMPLIFIED":
                return base + (
                    "Domestic manufacturing of eligible consumer and electrical goods can utilize Scheme-I: Simplified Fast-Track Procedure (Option 2). "
                    "Under this route, a license is granted within 30 days based on self-declaration and complete passing test reports from a BIS-recognized or NABL-accredited laboratory, "
                    "followed by a post-grant verification inspection within 30-90 days."
                )
            elif scheme_code == "ECO_MARK":
                return base + (
                    "Environment-friendly consumer products fall under the ECO Mark Scheme integrated under Scheme-I. "
                    "Products must meet both the primary Indian Standard quality specifications (ISI mark) and specific MoEFCC environmental criteria (resource efficiency, non-toxic formulations, recyclable packaging)."
                )
            elif scheme_code == "SCHEME_II_CRS":
                return base + (
                    "Electronic and Information Technology Goods are governed under Scheme-II: Compulsory Registration Scheme (CRS) notified by MeitY / MNRE. "
                    "This route does not require a preliminary factory audit; instead, compliance is achieved via sample testing at a BIS-recognized Indian laboratory "
                    "followed by self-declaration of conformity registration (R-XXXXXXXX) on the CRS portal."
                )
            elif scheme_code == "SCHEME_III_COC":
                return base + (
                    "Custom consignments, imported project lots, and specialized assemblies where continuous factory marking is not viable fall under Scheme-III: Certificate of Conformity (CoC). "
                    "A certificate is granted specifically for the inspected batch quantity following statistical sampling and laboratory verification."
                )
            elif scheme_code == "SCHEME_IV_MSCS":
                return base + (
                    "Organizational systems and operational frameworks fall under Scheme-IV: Management Systems Certification Scheme (MSCS) governed under Schedule-IV of the 2018 Regulations. "
                    "This includes statutory certification for ISO 9001 (QMS), ISO 14001 (EMS), IS/ISO 22000 (FSMS), ISO 45001 (OHSMS), ISO 50001 (EnMS), and ISO 13485 (Medical Devices)."
                )
            elif scheme_code == "SCHEME_X_CAPITAL_GOODS":
                return base + (
                    "Industrial machinery, heavy electrical power apparatus, and specialized capital goods fall under Scheme-X (Conformity Assessment Regulations, Schedule-X). "
                    "This streamlined route evaluates a comprehensive Technical Construction File (TCF), on-site/in-situ testing capabilities, and safety design declarations."
                )
            elif scheme_code == "HALLMARKING":
                return base + (
                    "Precious metal jewellery (Gold and Silver) is regulated under the mandatory Hallmarking Scheme under Section 14/15 of the BIS Act 2016. "
                    "Jewellers register online and submit batches to BIS-recognized Assaying & Hallmarking Centres (AHC) for assaying and 6-digit Hallmark Unique Identification (HUID) laser marking."
                )
            elif scheme_code == "LABORATORY_RECOGNITION":
                return base + (
                    "Testing facilities and commercial laboratories seeking empanelment for BIS testing fall under the Laboratory Recognition Scheme (LRS / LIMS) governed under Rule 32 of BIS Rules, 2018."
                )
            else:
                return base + (
                    "Domestic manufacturing of electrical, mechanical, chemical, food, or consumer products generally falls under Scheme-I: Product Certification — Normal Procedure (ISI Mark). "
                    "This route requires in-house testing facilities, preliminary factory quality management audit, independent sample drawl, and complete laboratory testing before the grant of a CM/L license."
                )


    def _build_steps(
        self,
        scheme: Dict[str, Any],
        product_display: str,
        std_number: Optional[str],
        is_qco: bool,
        qco_order: Optional[str],
        is_foreign: bool,
        citations: List[CitationItem],
        lang: str
    ) -> List[RoadmapStepItem]:
        std_text = std_number or "Applicable Indian Standard"

        if lang == "hi":
            return [
                RoadmapStepItem(
                    step_number=1,
                    title=f"लागू भारतीय मानक ({std_text}) और दायरे की पहचान",
                    description=f"{product_display} के लिए सटीक भारतीय मानक (IS) और तकनीकी सीमाओं की पहचान करें। सामग्री विनिर्देश, सुरक्षा आवश्यकताएं और परीक्षण मानक निर्धारित करें।",
                    status_badge="चरण 1: मानक पहचान",
                    checklist=[
                        f"बीआईएस बिक्री पोर्टल से {std_text} की आधिकारिक प्रति प्राप्त करें",
                        "उत्पाद की रेटिंग और तकनीकी विशेषताओं का मानक के दायरे से मिलान करें",
                        "संबंधित संशोधनों और नवीनतम परिशिष्टों का सत्यापन करें"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=2,
                    title="गुणवत्ता नियंत्रण आदेश (QCO) और अनिवार्यता की जांच",
                    description=f"जांचें कि क्या संबंधित मंत्रालय द्वारा {product_display} पर अनिवार्य QCO लागू किया गया है। {'अनिवार्य QCO अधिसूचित: ' + qco_order if is_qco else 'यदि QCO अधिसूचित नहीं है, तो यह स्वैच्छिक प्रमाणन है।'}",
                    status_badge="अनिवार्य QCO" if is_qco else "मानक सत्यापन",
                    checklist=[
                        "आधिकारिक बीआईएस अनिवार्य उत्पादों की सूची की जांच करें",
                        "लागू होने की समय-सीमा और एमएसएमई छूट शर्तों की समीक्षा करें",
                        "बिना प्रमाणन के आयात/बिक्री पर विधिक प्रतिबंधों को समझें"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=3,
                    title=f"प्रमाणन योजना ({scheme.get('name', 'योजना-I')}) एवं दिशा-निर्देशों की समीक्षा",
                    description=f"निर्धारित योजना के तहत उत्पाद-विशिष्ट निरीक्षण एवं परीक्षण योजना (SIT) और पात्रता मानदंडों की समीक्षा करें।",
                    status_badge=scheme.get("scheme_code", "SCHEME_I_ISI_NORMAL"),
                    checklist=[
                        "उत्पाद-विशिष्ट बीआईएस दिशा-निर्देश (Product Specific Guidelines) डाउनलोड करें",
                        "निरीक्षण और परीक्षण योजना (SIT) के अनुसार इन-हाउस लैब सेटअप करें",
                        "विदेशी निर्माताओं के लिए अधिकृत भारतीय प्रतिनिधि (AIR) की नियुक्ति करें" if is_foreign else "कारखाना पंजीकरण और विनिर्माण मशीनरी का दस्तावेजीकरण करें"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=4,
                    title="दस्तावेज तैयार करना एवं अनुरूपता परीक्षण व्यवस्था",
                    description=f"आवश्यक कानूनी, तकनीकी और परीक्षण दस्तावेज तैयार करें तथा बीआईएस मान्यता प्राप्त प्रयोगशाला में नमूना परीक्षण कराएं।",
                    status_badge="दस्तावेजीकरण & परीक्षण",
                    checklist=[
                        "परीक्षण उपकरणों के वैध अंशांकन (Calibration) प्रमाण पत्र प्राप्त करें",
                        "मान्यता प्राप्त बीआईएस लैब में औपचारिक नमूना परीक्षण करवाएं",
                        "मानक के सभी खंडों का अनुपालन करने वाली वैध परीक्षण रिपोर्ट प्राप्त करें"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=5,
                    title="मानक ऑनलाइन / सीआरएस पोर्टल पर ऑनलाइन आवेदन",
                    description="आधिकारिक बीआईएस पोर्टल (ManakOnline या CRS Portal) पर निर्धारित आवेदन शुल्क और दस्तावेजों के साथ आवेदन जमा करें।",
                    status_badge="पोर्टल ई-फाइलिंग",
                    checklist=[
                        "ManakOnline पोर्टल पर खाता बनाएं और ई-आवेदन भरें",
                        "निर्धारित आवेदन और ऑडिट शुल्क का ऑनलाइन भुगतान करें",
                        "सभी तकनीकी रिपोर्ट और शपथ पत्र पोर्टल पर अपलोड करें"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=6,
                    title="फैक्ट्री ऑडिट, लाइसेंस अनुदान एवं निरंतर अनुपालन",
                    description="बीआईएस अधिकारियों द्वारा कारखाना निरीक्षण (Scheme-I/FMCS) अथवा दस्तावेज सत्यापन के बाद सीएम/एल लाइसेंस अथवा सीआरएस पंजीकरण संख्या प्राप्त करें।",
                    status_badge="लाइसेंस अनुदान & मार्किंग",
                    checklist=[
                        "बीआईएस अधिकारी के ऑन-साइट फैक्ट्री निरीक्षण की सुविधा प्रदान करें",
                        "लाइसेंस मिलने पर निर्धारित प्रारूप में ISI / CRS मार्क लगाएं",
                        "वार्षिक नवीनीकरण और बाजार निगरानी परीक्षण नियमों का पालन करें"
                    ],
                    citations=[]
                )
            ]
        elif lang == "ta":
            return [
                RoadmapStepItem(
                    step_number=1,
                    title=f"பொருந்தக்கூடிய இந்திய தரநிலையை ({std_text}) அடையாளம் காணுதல்",
                    description=f"{product_display} க்கான சரியான இந்திய தரநிலை மற்றும் பாதுகாப்பு விதிகளை அடையாளம் காணவும்.",
                    status_badge="படி 1: தரநிலை அடையாளம்",
                    checklist=[
                        f"BIS இலிருந்து {std_text} அதிகாரப்பூர்வ நகலைப் பெறவும்",
                        "தயாரிப்பு விவரக்குறிப்புகளை தரநிலையின் விதிகளுடன் ஒப்பிடவும்",
                        "சமீபத்திய திருத்தங்கள் மற்றும் மறுஆய்வு நிலையை சரிபார்க்கவும்"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=2,
                    title="தரக் கட்டுப்பாட்டு ஆணை (QCO) சரிபார்த்தல்",
                    description=f"இந்த தயாரிப்புக்கு அமைச்சகத்தின் கட்டாய தரக் கட்டுப்பாட்டு ஆணை உள்ளதா என சரிபார்க்கவும். {'கட்டாய QCO ஆணை: ' + qco_order if is_qco else 'அரசாணை இல்லாத வரை இது விருப்ப தரநிலையாகும்.'}",
                    status_badge="கட்டாய QCO" if is_qco else "தரநிலை சரிபார்ப்பு",
                    checklist=[
                        "BIS கட்டாய தயாரிப்புகள் பதிவேட்டை சரிபார்க்கவும்",
                        "அமலாக்க தேதிகள் மற்றும் தளர்வு விதிகளை மதிப்பாய்வு செய்யவும்",
                        "சான்றிதழ் இல்லாத தயாரிப்புகளின் இறக்குமதி தடைகளை அறியவும்"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=3,
                    title=f"சான்றிதழ் திட்டத்தை ({scheme.get('name', 'திட்டம்-I')}) மதிப்பாய்வு செய்தல்",
                    description="பொருந்தக்கூடிய சான்றிதழ் திட்டம் மற்றும் தயாரிப்பு சார்ந்த வழிகாட்டுதல்களை மதிப்பாய்வு செய்யவும்.",
                    status_badge=scheme.get("scheme_code", "SCHEME_I_ISI_NORMAL"),
                    checklist=[
                        "BIS தயாரிப்பு சார்ந்த வழிகாட்டுதல்களைப் பதிவிறக்கவும்",
                        "ஆய்வு மற்றும் சோதனை திட்டத்தின்படி (SIT) உள் ஆய்வகத்தை அமைக்கவும்",
                        "வெளிநாட்டு நிறுவனங்கள் இந்திய பிரதிநிதியை (AIR) நியமிக்கவும்" if is_foreign else "தொழிற்சாலை பதிவு ஆவணங்களை சரிபார்க்கவும்"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=4,
                    title="ஆவணங்கள் மற்றும் மாதிரி சோதனை ஏற்பாடுகள்",
                    description="தேவையான தொழில்நுட்ப கோப்புகளை தயார் செய்து BIS அங்கீகரிக்கப்பட்ட ஆய்வகத்தில் மாதிரி சோதனை நடத்தவும்.",
                    status_badge="ஆவணங்கள் & சோதனை",
                    checklist=[
                        "சோதனை உபகரணங்களுக்கான அளவீட்டு அளவுத்திருத்த (Calibration) சான்றிதழ்களைப் பெறவும்",
                        "அங்கீகரிக்கப்பட்ட ஆய்வகத்தில் முழுமையான மாதிரி பரிசோதனை நடத்தவும்",
                        "அனைத்து விதிகளுக்கும் இணங்கும் சோதனை அறிக்கையைப் பெறவும்"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=5,
                    title="BIS ManakOnline போர்ட்டலில் விண்ணப்பம் சமர்ப்பித்தல்",
                    description="ManakOnline அல்லது CRS போர்ட்டலில் தேவையான கட்டணங்களுடன் விண்ணப்பத்தை சமர்ப்பிக்கவும்.",
                    status_badge="போர்ட்டல் விண்ணப்பம்",
                    checklist=[
                        "ManakOnline போர்ட்டலில் பதிவு செய்து விவரங்களை பதிவேற்றவும்",
                        "விண்ணப்பம் மற்றும் ஆய்வு கட்டணங்களை செலுத்தவும்",
                        "தொழில்நுட்ப அறிக்கைகளை பதிவேற்றவும்"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=6,
                    title="தொழிற்சாலை தணிக்கை, உரிமம் வழங்குதல் மற்றும் இணக்கம்",
                    description="BIS தணிக்கைக்குப் பிறகு உரிமம் பெற்று தயாரிப்புகளில் ISI அல்லது CRS முத்திரையைப் பொறிக்கவும்.",
                    status_badge="உரிமம் & முத்திரை",
                    checklist=[
                        "BIS அதிகாரியின் தொழிற்சாலை ஆய்வை எளிதாக்கவும்",
                        "உரிமம் கிடைத்தவுடன் தயாரிப்புகளில் தரக் குறியீட்டைப் பொருத்தவும்",
                        "வருடாந்திர புதுப்பித்தல் மற்றும் சந்தை கண்காணிப்பு விதிகளுக்கு இணங்கவும்"
                    ],
                    citations=[]
                )
            ]
        else:
            return [
                RoadmapStepItem(
                    step_number=1,
                    title=f"Identify Applicable Indian Standard ({std_text}) & Technical Scope",
                    description=f"Define core technical parameters for {product_display} and confirm scope coverage under {std_text}. Review testing sequence, critical component ratings, and permissible tolerances.",
                    status_badge="Stage 1: Standard Identification",
                    checklist=[
                        f"Procure official authorized copy of {std_text} from BIS Standards Portal",
                        "Verify full product scope, rating thresholds, and classification clauses",
                        "Review latest gazetted amendments, corrigenda, and revision schedules"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=2,
                    title="Check Quality Control Order (QCO) Applicability & Enforcement Date",
                    description=f"Ascertain whether the relevant Line Ministry has issued a mandatory Quality Control Order under Section 16 of the BIS Act, 2016. {'Mandatory QCO Enforced: ' + qco_order if is_qco else 'Voluntary standard unless specifically notified by government regulation.'}",
                    status_badge="QCO Mandatory" if is_qco else "Standard Verified",
                    checklist=[
                        "Cross-reference the central mandatory certification registry on bis.gov.in",
                        "Verify enforcement effective date and MSME / startup transition exemptions",
                        "Confirm customs and domestic market legal obligations prior to dispatch"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=3,
                    title=f"Review Applicable Scheme ({scheme.get('name', 'Scheme-I')}) & Product Guidelines",
                    description="Examine the Scheme of Inspection and Testing (SIT) and product-specific guidelines prescribed by BIS for your product category.",
                    status_badge=scheme.get("scheme_code", "SCHEME_I_ISI_NORMAL"),
                    checklist=[
                        "Download official Product-Specific Guidelines from BIS Product Certification division",
                        "Establish in-house testing facility conforming strictly to the prescribed SIT",
                        "Nominate and execute legal agreement with Authorized Indian Representative (AIR)" if is_foreign else "Document manufacturing flow, machinery capacities, and factory establishment"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=4,
                    title="Prepare Required Documentation & Testing Arrangements",
                    description=f"Compile the technical dossier, verify calibration certificates of all in-house gauges, and conduct sample testing at a BIS-recognized / NABL testing laboratory.",
                    status_badge="Documentation & Testing",
                    checklist=[
                        "Obtain NABL-traceable calibration certificates for all measuring and test instruments",
                        "Submit production samples with technical construction files to a BIS-recognized lab",
                        "Acquire independent compliant Test Report satisfying all standard clauses"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=5,
                    title="Submit Application on Official ManakOnline / CRS Portal",
                    description="File formal application on the central Government of India BIS portal (ManakOnline or CRS) along with prescribed fees and test reports.",
                    status_badge="Portal E-Filing",
                    checklist=[
                        "Register entity on ManakOnline (manakonline.in) or CRS portal",
                        "Upload application form, technical dossier, factory layout, and test certificates",
                        "Remit prescribed application and preliminary assessment fees through official gateway"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=6,
                    title="Factory Audit, License Grant, Labeling & Ongoing Compliance",
                    description="Facilitate on-site factory audit by BIS inspecting officer (for Scheme-I/FMCS) or technical review, obtain CM/L License or Registration Number, and affix the Standard Mark.",
                    status_badge="Grant of License / Marking",
                    checklist=[
                        "Facilitate factory audit and witness sample drawl by BIS inspecting officer",
                        "Furnish Performance Bank Guarantee and execute license agreement upon approval",
                        "Affix the official Standard Mark (ISI mark / CRS R-Number) with license number on product and packaging",
                        "Maintain routine testing registers and adhere to annual license renewal schedules"
                    ],
                    citations=[]
                )
            ]

    def _build_document_checklist(
        self,
        scheme_code: str,
        is_foreign: bool,
        has_standard: bool,
        lang: str
    ) -> List[DocumentChecklistItem]:
        checklist: List[DocumentChecklistItem] = []

        # Category 1: LEGAL_INCORPORATION
        if lang == "hi":
            checklist.extend([
                DocumentChecklistItem(
                    item="कारखाना पंजीकरण प्रमाण पत्र / उद्योग आधार / एमएसएमई पंजीकरण / कंपनी निगमन प्रमाण पत्र",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="आधिकारिक बीआईएस दिशानिर्देशों के अनुसार अनिवार्य विधिक प्रमाण"
                ),
                DocumentChecklistItem(
                    item="जीएसटी पंजीकरण प्रमाण पत्र और पैन कार्ड की प्रति",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="घरेलू विनिर्माताओं के लिए आवश्यक"
                ),
                DocumentChecklistItem(
                    item="व्यापार चिह्न (Trade Mark / Brand) पंजीकरण प्रमाण पत्र या प्राधिकरण पत्र",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="ब्रांड स्वामित्व का आधिकारिक प्रमाण"
                ),
                DocumentChecklistItem(
                    item="कंपनी के अधिकृत हस्ताक्षरकर्ता का बोर्ड प्रस्ताव अथवा पावर ऑफ अटॉर्नी",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=False,
                    guidance_type="GENERAL_PREPARATION",
                    note="पोर्टल सबमिशन के लिए सामान्य तैयारी सुझाव"
                )
            ])
        elif lang == "ta":
            checklist.extend([
                DocumentChecklistItem(
                    item="தொழிற்சாலை பதிவு சான்றிதழ் / MSME பதிவு / நிறுவன ஒருங்கிணைப்பு ஆவணம்",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="அதிகாரப்பூர்வ BIS வழிகாட்டுதல்களின்படி கட்டாய ஆவணம்"
                ),
                DocumentChecklistItem(
                    item="GST பதிவு சான்றிதழ் மற்றும் PAN அட்டை நகல்",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="உள்நாட்டு உற்பத்தியாளர்களுக்கு கட்டாயம்"
                ),
                DocumentChecklistItem(
                    item="வர்த்தக முத்திரை (Trade Mark) பதிவு சான்றிதழ் அல்லது அனுமதி கடிதம்",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="பிராண்ட் உரிமையின் அதிகாரப்பூர்வ சான்று"
                )
            ])
        else:
            checklist.extend([
                DocumentChecklistItem(
                    item="Factory Registration / Business License / Certificate of Incorporation / Udhyam MSME Registration",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Mandatory proof of legal establishment under BIS (Conformity Assessment) Regulations"
                ),
                DocumentChecklistItem(
                    item="GST Registration Certificate and PAN Card Copy of the manufacturing unit",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Mandatory tax registration for domestic entities"
                ),
                DocumentChecklistItem(
                    item="Trademark Registration Certificate or Brand Authorization Agreement",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Required to prove legal ownership of the brand name marked on certified goods"
                ),
                DocumentChecklistItem(
                    item="Board Resolution or Power of Attorney authorizing the signatory to file on behalf of entity",
                    category="LEGAL_INCORPORATION",
                    is_verified_official=False,
                    guidance_type="GENERAL_PREPARATION",
                    note="General administrative preparation suggestion for portal e-filing"
                )
            ])

        # Category 2: TECHNICAL_FACILITY
        if lang == "hi":
            checklist.extend([
                DocumentChecklistItem(
                    item="विनिर्माण मशीनरी की विस्तृत सूची, क्षमता और मेक/मॉडल विवरण",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="उत्पादन क्षमता सत्यापन हेतु बीआईएस द्वारा अनिवार्य"
                ),
                DocumentChecklistItem(
                    item="कारखाने का लेआउट प्लान और निर्माण प्रक्रिया प्रवाह चार्ट (Process Flow Chart)",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="कच्चे माल से तैयार माल तक की गुणवत्ता नियंत्रण प्रक्रिया"
                ),
                DocumentChecklistItem(
                    item="योग्य गुणवत्ता नियंत्रण कर्मियों (QC Staff) के नियुक्ति पत्र एवं शैक्षणिक योग्यता प्रमाण पत्र",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="बीआईएस निरीक्षण और परीक्षण योजना (SIT) के तहत अनिवार्य"
                ),
                DocumentChecklistItem(
                    item="कच्चे माल के आपूर्तिकर्ताओं के साथ परीक्षण अनुबंध और गुणवत्ता विनिर्देश",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=False,
                    guidance_type="GENERAL_PREPARATION",
                    note="गुणवत्ता आश्वासन के लिए सामान्य तैयारी सुझाव"
                )
            ])
        elif lang == "ta":
            checklist.extend([
                DocumentChecklistItem(
                    item="உற்பத்தி இயந்திரங்களின் பட்டியல், திறன் மற்றும் விவரங்கள்",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="BIS தணிக்கைக்கு தேவையான அதிகாரப்பூர்வ ஆவணம்"
                ),
                DocumentChecklistItem(
                    item="தொழிற்சாலை வரைபடம் (Layout) மற்றும் உற்பத்தி செயல்முறை விளக்கப்படம் (Process Flowchart)",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="முழுமையான உற்பத்தி ஓட்டத்தின் சான்று"
                ),
                DocumentChecklistItem(
                    item="தரக் கட்டுப்பாட்டு பணியாளர்களின் நியமன கடிதங்கள் மற்றும் கல்வி சான்றிதழ்கள்",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="SIT விதிகளின்படி கட்டாய பணியாளர் தேவை"
                )
            ])
        else:
            checklist.extend([
                DocumentChecklistItem(
                    item="Complete List of Manufacturing Machinery with technical ratings, capacity, and operational status",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Mandatory official schedule to verify complete in-house manufacturing process"
                ),
                DocumentChecklistItem(
                    item="Plant Layout Plan and Step-by-Step Manufacturing Process Flowchart",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Required to demonstrate material flow from raw inspection to packaging"
                ),
                DocumentChecklistItem(
                    item="Quality Control Personnel appointment letters, organizational hierarchy, and technical degrees",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Mandatory under Scheme of Inspection & Testing (SIT) for competency verification"
                ),
                DocumentChecklistItem(
                    item="Standard Operating Procedures (SOP) and raw material test certificates from approved vendors",
                    category="TECHNICAL_FACILITY",
                    is_verified_official=False,
                    guidance_type="GENERAL_PREPARATION",
                    note="Recommended general preparation for smooth factory inspection audit"
                )
            ])

        # Category 3: TESTING_CALIBRATION
        if lang == "hi":
            checklist.extend([
                DocumentChecklistItem(
                    item="इन-हाउस प्रयोगशाला परीक्षण उपकरणों की पूरी सूची (SIT के अनुसार आवश्यक)",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="मानक के अनुरूप सभी नियमित परीक्षणों के लिए आवश्यक"
                ),
                DocumentChecklistItem(
                    item="NABL मान्यता प्राप्त प्रयोगशाला से जारी वैध अंशांकन प्रमाण पत्र (Calibration Certificates)",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="सभी परीक्षण उपकरणों के लिए 1 वर्ष से कम पुराना होना चाहिए"
                ),
                DocumentChecklistItem(
                    item="बीआईएस मान्यता प्राप्त प्रयोगशाला से स्वतंत्र नमूना परीक्षण रिपोर्ट (CRS के लिए अनिवार्य)",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="योजना-II (CRS) में 90 दिनों के भीतर की परीक्षण रिपोर्ट आवश्यक"
                ),
                DocumentChecklistItem(
                    item="दैनिक बैच परीक्षण लॉगबुक और नमूना रिकॉर्ड प्रारूप",
                    category="TESTING_CALIBRATION",
                    is_verified_official=False,
                    guidance_type="GENERAL_PREPARATION",
                    note="फैक्ट्री ऑडिट के दौरान निरीक्षण के लिए सामान्य तैयारी सुझाव"
                )
            ])
        elif lang == "ta":
            checklist.extend([
                DocumentChecklistItem(
                    item="உள்நாட்டு ஆய்வக சோதனை உபகரணங்களின் பட்டியல் (SIT தேவைகளின்படி)",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="SIT வழிகாட்டுதல்களின்படி கட்டாயம்"
                ),
                DocumentChecklistItem(
                    item="NABL அங்கீகரிக்கப்பட்ட ஆய்வகத்திலிருந்து செல்லுபடியாகும் அளவுத்திருத்த (Calibration) சான்றிதழ்கள்",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="அனைத்து சோதனை கருவிகளுக்கும் கட்டாயம்"
                ),
                DocumentChecklistItem(
                    item="BIS அங்கீகரிக்கப்பட்ட ஆய்வகத்திலிருந்து பெறப்பட்ட மாதிரி சோதனை அறிக்கை",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="CRS மற்றும் வகை சோதனைக்கான அதிகாரப்பூர்வ அறிக்கை"
                )
            ])
        else:
            checklist.extend([
                DocumentChecklistItem(
                    item="List of In-house Testing Equipment matching all tests prescribed in the BIS Scheme of Inspection & Testing (SIT)",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Mandatory official requirement for Scheme-I / FMCS licensing"
                ),
                DocumentChecklistItem(
                    item="Valid Calibration Certificates issued by NABL-accredited calibration laboratories for all test equipment",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Must be within validity period (typically within 12 months) with traceability records"
                ),
                DocumentChecklistItem(
                    item="Independent Test Report from a BIS-Recognized Testing Laboratory (mandatory within 90 days for CRS)",
                    category="TESTING_CALIBRATION",
                    is_verified_official=True,
                    guidance_type="VERIFIED_OFFICIAL",
                    note="Official requirement verifying full clause compliance"
                ),
                DocumentChecklistItem(
                    item="Routine batch test logbook, rejection records, and sample retention registers",
                    category="TESTING_CALIBRATION",
                    is_verified_official=False,
                    guidance_type="GENERAL_PREPARATION",
                    note="General operational quality preparation suggestion for on-site audit readiness"
                )
            ])

        # Category 4: AIR_FOREIGN (If foreign or FMCS / CRS foreign OEM)
        if is_foreign or scheme_code in ("SCHEME_I_FMCS", "SCHEME_IV_FMCS"):

            if lang == "hi":
                checklist.extend([
                    DocumentChecklistItem(
                        item="अधिकृत भारतीय प्रतिनिधि (AIR) का औपचारिक नामांकन और कानूनी समझौता (Form-V / Agreement)",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="विदेशी निर्माताओं के लिए बीआईएस नियमों के तहत अनिवार्य विधिक शर्त"
                    ),
                    DocumentChecklistItem(
                        item="अधिकृत भारतीय प्रतिनिधि (AIR) का पहचान प्रमाण, पैन कार्ड एवं भारतीय पता प्रमाण",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="AIR भारत का निवासी नागरिक या पंजीकृत भारतीय इकाई होना चाहिए"
                    ),
                    DocumentChecklistItem(
                        item="परफॉर्मेंस बैंक गारंटी (PBG - USD 10,000) का अंडरटेकिंग (FMCS हेतु)",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="एफएमसीएस योजना के तहत लाइसेंस अनुदान से पूर्व अनिवार्य"
                    ),
                    DocumentChecklistItem(
                        item="विदेशी विनिर्माण इकाई का स्थानीय उद्योग/कारखाना निगमन लाइसेंस",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="मूल देश के सक्षम प्राधिकरण द्वारा जारी"
                    )
                ])
            elif lang == "ta":
                checklist.extend([
                    DocumentChecklistItem(
                        item="அங்கீகரிக்கப்பட்ட இந்திய பிரதிநிதி (AIR) நியமன ஆவணம் மற்றும் சட்ட ஒப்பந்தம்",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="வெளிநாட்டு உற்பத்தியாளர்களுக்கு BIS சட்டப்படி கட்டாயம்"
                    ),
                    DocumentChecklistItem(
                        item="AIR பிரதிநிதியின் இந்திய அடையாள சான்று மற்றும் முகவரி சான்று",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="இந்தியாவில் வசிக்கும் பிரதிநிதிக்கு கட்டாயம்"
                    ),
                    DocumentChecklistItem(
                        item="வங்கி உத்தரவாதம் (PBG - USD 10,000) உறுதிமொழி (FMCS திட்டத்திற்கு)",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="FMCS உரிமத்திற்கு கட்டாயம்"
                    )
                ])
            else:
                checklist.extend([
                    DocumentChecklistItem(
                        item="Authorized Indian Representative (AIR) Legal Nomination Agreement and Affidavit (Form-V)",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="Mandatory statutory requirement under BIS Act 2016 for all foreign manufacturing applicants"
                    ),
                    DocumentChecklistItem(
                        item="AIR Proof of Identity, PAN card, and Indian Business/Residential Address Proof",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="AIR must be an Indian resident or registered Indian entity responsible for BIS compliance"
                    ),
                    DocumentChecklistItem(
                        item="Performance Bank Guarantee (PBG) of USD 10,000 from an RBI-approved scheduled bank (for FMCS)",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="Mandatory financial indemnity required prior to grant of Scheme-IV FMCS license"
                    ),
                    DocumentChecklistItem(
                        item="Foreign Factory Legal Incorporation / Commercial Registry License from country of origin",
                        category="AIR_FOREIGN",
                        is_verified_official=True,
                        guidance_type="VERIFIED_OFFICIAL",
                        note="Must be notarized/apostilled where required by BIS Foreign Manufacturers Department"
                    )
                ])

        return checklist


certification_navigator_service = CertificationNavigatorService()
