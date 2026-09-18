from typing import Optional, List, Dict, Any
from app.schemas.intelligence import (
    CertificationRoadmapRequest,
    CertificationRoadmapResponse,
    RoadmapStepItem
)
from app.schemas.chat import CitationItem
from app.db.seed_intelligence import VERIFIED_STANDARDS, VERIFIED_SCHEMES


class CertificationNavigatorService:
    """
    BIS Certification Navigator Service.
    Builds a guided 5-step roadmap correlating product characteristics, applicable standards,
    certification schemes (ISI Mark, CRS, FMCS), laboratory testing requirements, and application procedures
    with full multilingual localization support (English, Hindi, Tamil).
    """

    def generate_roadmap(self, request: CertificationRoadmapRequest) -> CertificationRoadmapResponse:
        product_query = (request.product_name or "").strip()
        std_query = (request.standard_number or "").strip()
        scheme_query = (request.scheme_code or "").strip()
        lang = (request.language or "en").lower()

        # Resolve Standard
        matched_std: Optional[Dict[str, Any]] = None
        if std_query:
            matched_std = next(
                (s for s in VERIFIED_STANDARDS if std_query.lower() in s["standard_number"].lower()),
                None
            )
        elif product_query:
            matched_std = next(
                (s for s in VERIFIED_STANDARDS if any(
                    w in f"{s['title']} {s.get('scope_summary', '')}".lower()
                    for w in product_query.lower().split() if len(w) > 3
                )),
                None
            )

        # Resolve Scheme
        matched_scheme: Optional[Dict[str, Any]] = None
        if scheme_query:
            matched_scheme = next(
                (sc for sc in VERIFIED_SCHEMES if scheme_query.lower() in sc["scheme_code"].lower() or scheme_query.lower() in sc["name"].lower()),
                None
            )
        elif matched_std:
            # IT / Electronics defaults to CRS, others to Scheme-I ISI
            if "information technology" in matched_std.get("division", "").lower() or "13252" in matched_std["standard_number"]:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_II_CRS"), None)
            else:
                matched_scheme = next((sc for sc in VERIFIED_SCHEMES if sc["scheme_code"] == "SCHEME_I_ISI"), None)
        else:
            matched_scheme = VERIFIED_SCHEMES[0]

        product_display = product_query or (matched_std["title"] if matched_std else "Specified Product")
        std_number = matched_std["standard_number"] if matched_std else (std_query or "Applicable Indian Standard")
        is_qco = matched_std["is_qco_mandatory"] if matched_std else False
        qco_order = matched_std.get("qco_order_number") if matched_std else None

        citations: List[CitationItem] = []
        if matched_std:
            citations.append(CitationItem(
                id=1,
                standard_number=matched_std["standard_number"],
                title=matched_std["title"],
                clause="1.1 Scope",
                page=1,
                snippet=matched_std.get("scope_summary", matched_std["title"])[:200],
                source="BIS"
            ))

        # Localized step building based on language
        if lang == "ta":
            # --- TAMIL LOCALIZATION ---
            scheme_name_display = "திட்டம்-I: தயாரிப்பு சான்றிதழ் (ISI முத்திரை)"
            if matched_scheme and matched_scheme.get("scheme_code") == "SCHEME_II_CRS":
                scheme_name_display = "திட்டம்-II: கட்டாய பதிவு திட்டம் (CRS)"
            elif matched_scheme and matched_scheme.get("scheme_code") == "SCHEME_IV_FMCS":
                scheme_name_display = "வெளிநாட்டு உற்பத்தியாளர்கள் சான்றிதழ் திட்டம் (FMCS)"

            disclaimer_text = (
                "அறிவிப்பு: இந்த வழிகாட்டி கிடைக்கக்கூடிய BIS ஆவணங்களிலிருந்து உருவாக்கப்பட்ட ஒரு தகவல் வழிகாட்டியாகும். "
                "இது அதிகாரப்பூர்வ BIS ஒப்புதல், அங்கீகாரம் அல்லது சட்டப்பூர்வ சான்றிதழ் அல்ல."
            )

            steps = [
                RoadmapStepItem(
                    step_number=1,
                    title="தயாரிப்பு மற்றும் தொழில்நுட்ப விவரக்குறிப்புகளை அடையாளம் காணுதல்",
                    description=(
                        f"{product_display} க்கான முக்கிய அளவுருக்களை வரையறுக்கவும் (பொருட்கள், "
                        f"மின்னழுத்தம்/மின்னோட்டம், பரிமாணங்கள் மற்றும் பாதுகாப்பு பாகங்கள்)."
                    ),
                    status_badge="விவரக்குறிப்பு வரையறுக்கப்பட்டது",
                    checklist=[
                        "விரிவான தயாரிப்பு விவரக்குறிப்பு தாளை தயார் செய்யவும்",
                        "அனைத்து முக்கிய உதிரிபாகங்கள் மற்றும் பாதுகாப்பு பாகங்களை பட்டியலிடவும்",
                        "உள்நாட்டு உற்பத்தி அல்லது வெளிநாட்டு உற்பத்தி வழியை உறுதிப்படுத்தவும்"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=2,
                    title=f"பொருந்தக்கூடிய இந்திய தரநிலையை சரிபார்த்தல் ({std_number})",
                    description=(
                        f"{std_number} தரநிலைக்கு எதிரான இணக்கத் தேவைகளை மதிப்பிடவும். "
                        f"{'கட்டாய தரக் கட்டுப்பாட்டு ஆணை (QCO) பொருந்தும்: ' + qco_order if is_qco else 'அரசாணை இல்லாத வரை இது விருப்ப தரநிலையாகும்.'}"
                    ),
                    status_badge="கட்டாய QCO ஆணை" if is_qco else "தரநிலை உறுதிப்படுத்தப்பட்டது",
                    checklist=[
                        f"BIS இடமிருந்து {std_number} அதிகாரப்பூர்வ நகலை பெறவும்",
                        "நோக்கம் மற்றும் பிரிவு வாரியான விதிகளை சரிபார்க்கவும்",
                        "சமீபத்திய திருத்தங்கள் மற்றும் மறுஆய்வு நிலையை சரிபார்க்கவும்"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=3,
                    title=f"சான்றிதழ் திட்டத்தை தீர்மானித்தல் ({scheme_name_display})",
                    description="BIS தயாரிப்பு சான்றிதழ் திட்டம் மற்றும் தேவையான விண்ணப்ப ஆவணங்கள்.",
                    status_badge=matched_scheme.get("scheme_code", "SCHEME_I_ISI") if matched_scheme else "SCHEME_I_ISI",
                    checklist=[
                        "தொழிற்சாலை பதிவு / வணிக உரிமம்",
                        "இயந்திரங்கள் மற்றும் உற்பத்தி உபகரணங்கள் பட்டியல்",
                        "தரக் கட்டுப்பாட்டு பணியாளர்களின் தகுதிகள் மற்றும் சோதனை வசதிகள்"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=4,
                    title="BIS அங்கீகரிக்கப்பட்ட ஆய்வகத்தில் மாதிரி சோதனை",
                    description=(
                        f"உற்பத்தி மாதிரிகளை எடுத்து {std_number} விதிகளின்படி முழுமையான "
                        f"சோதனைக்காக BIS அங்கீகரிக்கப்பட்ட / NABL ஆய்வகத்திற்கு சமர்ப்பிக்கவும்."
                    ),
                    status_badge="சோதனை & மதிப்பீடு",
                    checklist=[
                        f"{std_number} க்கான அங்கீகரிக்கப்பட்ட ஆய்வகத்தைத் தேர்ந்தெடுக்கவும்",
                        "தொழில்நுட்ப ஆவணக் கோப்புடன் சோதனை மாதிரிகளை சமர்ப்பிக்கவும்",
                        "அனைத்து விதிகளுக்கும் இணங்கும் செல்லுபடியாகும் சோதனை அறிக்கையை பெறவும்"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=5,
                    title="BIS ManakOnline போர்ட்டலில் விண்ணப்பம் சமர்ப்பித்தல்",
                    description="ManakOnline போர்ட்டலில் சோதனை அறிக்கைகள் மற்றும் கட்டணங்களுடன் விண்ணப்பத்தை சமர்ப்பிக்கவும்.",
                    status_badge="உரிமம் / பதிவு வழங்குதல்",
                    checklist=[
                        "ManakOnline போர்ட்டலில் பதிவு செய்து விண்ணப்பத்தை பதிவேற்றவும்",
                        "விண்ணப்பம் மற்றும் மதிப்பீட்டுக் கட்டணங்களைச் செலுத்தவும்",
                        "BIS தொழிற்சாலை தணிக்கை அல்லது ஆவண ஆய்வை எளிதாக்கவும்",
                        "உரிமம் வழங்கப்பட்டதும் உரிம எண்ணுடன் BIS முத்திரையை பொருத்தவும்"
                    ],
                    citations=[]
                )
            ]
        elif lang == "hi":
            # --- HINDI LOCALIZATION ---
            scheme_name_display = "योजना-I: उत्पाद प्रमाणन (ISI मार्क)"
            if matched_scheme and matched_scheme.get("scheme_code") == "SCHEME_II_CRS":
                scheme_name_display = "योजना-II: अनिवार्य पंजीकरण योजना (CRS)"
            elif matched_scheme and matched_scheme.get("scheme_code") == "SCHEME_IV_FMCS":
                scheme_name_display = "विदेशी निर्माता प्रमाणन योजना (FMCS)"

            disclaimer_text = (
                "सूचना: यह रोडमैप बीआईएस दस्तावेजों से तैयार किया गया एक मार्गदर्शन है। "
                "यह आधिकारिक बीआईएस अनुमोदन, प्राधिकरण या कानूनी प्रमाण पत्र नहीं है।"
            )

            steps = [
                RoadmapStepItem(
                    step_number=1,
                    title="उत्पाद और तकनीकी विनिर्देशों की पहचान करें",
                    description=(
                        f"{product_display} के लिए प्रमुख मापदंडों को परिभाषित करें, जिसमें सामग्री, "
                        f"रेटेड वोल्टेज/करंट, आयाम और सुरक्षा घटक शामिल हैं।"
                    ),
                    status_badge="विनिर्देश परिभाषित",
                    checklist=[
                        "विस्तृत उत्पाद विनिर्देश शीट तैयार करें",
                        "सभी उप-घटकों और महत्वपूर्ण सुरक्षा भागों की सूची बनाएं",
                        "घरेलू निर्माण या विदेशी निर्माण मार्ग की पुष्टि करें"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=2,
                    title=f"लागू भारतीय मानक ({std_number}) सत्यापित करें",
                    description=(
                        f"{std_number} के अनुरूपता आवश्यकताओं का आकलन करें। "
                        f"{'अनिवार्य गुणवत्ता नियंत्रण आदेश (QCO) लागू है: ' + qco_order if is_qco else 'जब तक अधिसूचित न हो, यह स्वैच्छिक मानक है।'}"
                    ),
                    status_badge="अनिवार्य QCO" if is_qco else "मानक निर्धारित",
                    checklist=[
                        f"बीआईएस से {std_number} की आधिकारिक प्रति प्राप्त करें",
                        "दायरा और खंड-दर-खंड आवश्यकताओं का सत्यापन करें",
                        "नवीनतम संशोधनों और स्थिति की जांच करें"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=3,
                    title=f"प्रमाणन योजना का निर्धारण ({scheme_name_display})",
                    description="बीआईएस उत्पाद प्रमाणन योजना और आवश्यक आवेदन दस्तावेज।",
                    status_badge=matched_scheme.get("scheme_code", "SCHEME_I_ISI") if matched_scheme else "SCHEME_I_ISI",
                    checklist=[
                        "फैक्टरी पंजीकरण / व्यवसाय लाइसेंस",
                        "मशीनरी और निर्माण उपकरण सूची",
                        "गुणवत्ता नियंत्रण कर्मियों की योग्यता और प्रयोगशाला उपकरण"
                    ],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=4,
                    title="बीआईएस मान्यता प्राप्त प्रयोगशाला में अनुरूपता परीक्षण",
                    description=(
                        f"उत्पादन नमूने लें और {std_number} में निर्धारित पूर्ण परीक्षण के लिए "
                        f"बीआईएस-मान्यता प्राप्त / NABL प्रयोगशाला में जमा करें।"
                    ),
                    status_badge="परीक्षण और मूल्यांकन",
                    checklist=[
                        f"{std_number} के लिए मान्यता प्राप्त परीक्षण लैब चुनें",
                        "तकनीकी फाइल के साथ परीक्षण नमूने जमा करें",
                        "सभी खंडों का अनुपालन करने वाली वैध परीक्षण रिपोर्ट प्राप्त करें"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=5,
                    title="बीआईएस मानक ऑनलाइन पोर्टल पर आवेदन जमा करना",
                    description="मानक ऑनलाइन पोर्टल पर परीक्षण रिपोर्ट और शुल्क के साथ औपचारिक आवेदन जमा करें।",
                    status_badge="लाइसेंस / पंजीकरण अनुदान",
                    checklist=[
                        "मानक ऑनलाइन पोर्टल पर रजिस्टर और आवेदन अपलोड करें",
                        "निर्धारित आवेदन और मूल्यांकन शुल्क का भुगतान करें",
                        "बीआईएस फैक्टरी ऑडिट या तकनीकी जांच की सुविधा दें",
                        "लाइसेंस प्राप्त होने पर लाइसेंस नंबर के साथ मानक चिह्न लगाएं"
                    ],
                    citations=[]
                )
            ]
        else:
            # --- ENGLISH (DEFAULT) ---
            scheme_name_display = matched_scheme.get("name") if matched_scheme else "Scheme-I: Product Certification (ISI Mark)"
            disclaimer_text = (
                "Notice: This roadmap is an informative navigation guide generated from available BIS documentation. "
                "It does not constitute official BIS approval, authorization, or legal certification."
            )

            steps = [
                RoadmapStepItem(
                    step_number=1,
                    title="Identify Product & Technical Specifications",
                    description=(
                        f"Define key parameters for {product_display} including materials, rated voltage/current, "
                        f"dimensions, intended operational environment, and safety-critical components."
                    ),
                    status_badge="Specification Defined",
                    checklist=[
                        "Prepare detailed product specification sheet",
                        "List all sub-components and critical insulation/safety parts",
                        "Confirm domestic manufacturing or foreign manufacturing route"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=2,
                    title=f"Verify Applicable Indian Standard ({std_number})",
                    description=(
                        f"Assess conformity requirements against {std_number}. "
                        f"{'Mandatory Quality Control Order (QCO) applies under: ' + qco_order if is_qco else 'Voluntary standard unless specifically notified by regulator.'}"
                    ),
                    status_badge="QCO Mandatory" if is_qco else "Standard Defined",
                    checklist=[
                        f"Obtain official copy of {std_number} from BIS",
                        "Verify scope coverage and clause-by-clause requirements",
                        "Check latest amendments and revision status"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=3,
                    title=f"Determine Certification Scheme ({scheme_name_display})",
                    description=matched_scheme.get("description", "BIS Product Certification Scheme.") if matched_scheme else "BIS Product Certification Scheme.",
                    status_badge=matched_scheme.get("scheme_code", "SCHEME_I_ISI") if matched_scheme else "SCHEME_I_ISI",
                    checklist=matched_scheme.get("required_documents_checklist", [
                        "Factory registration / Business license",
                        "Machinery and manufacturing equipment inventory",
                        "Quality control personnel qualifications"
                    ]) if matched_scheme else [],
                    citations=[]
                ),
                RoadmapStepItem(
                    step_number=4,
                    title="Conformity Testing at BIS Recognized Laboratory",
                    description=(
                        f"Draw representative production samples and submit to a BIS-recognized / NABL-accredited "
                        f"testing facility for full sequence testing as prescribed in {std_number}."
                    ),
                    status_badge="Testing & Evaluation",
                    checklist=[
                        "Select accredited lab with verified testing scope for " + std_number,
                        "Submit test samples along with technical construction file",
                        "Obtain valid Test Report complying with all clauses"
                    ],
                    citations=citations
                ),
                RoadmapStepItem(
                    step_number=5,
                    title="Application Filing on BIS ManakOnline / CRS Portal",
                    description=(
                        matched_scheme.get("application_procedure_summary", "Submit formal application on ManakOnline portal with test reports and fees.")
                        if matched_scheme else "Submit formal application on ManakOnline."
                    ),
                    status_badge="Grant of License / Registration",
                    checklist=[
                        "Register and upload application on ManakOnline portal",
                        "Remit prescribed application and evaluation fees",
                        "Facilitate BIS factory audit (for Scheme-I / FMCS) or CRS scrutiny (for Scheme-II)",
                        "Affix Standard Mark with License Number upon grant"
                    ],
                    citations=[]
                )
            ]

        return CertificationRoadmapResponse(
            product=product_display,
            standard_number=std_number if matched_std else None,
            applicable_scheme=matched_scheme.get("scheme_code") if matched_scheme else "SCHEME_I_ISI",
            scheme_name=scheme_name_display,
            is_mandatory_qco=is_qco,
            qco_order_number=qco_order,
            steps=steps,
            disclaimer=disclaimer_text,
            citations=citations
        )
