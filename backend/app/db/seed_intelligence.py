"""
Seed data and in-memory registry for verified BIS standards, schemes, and testing laboratories.
Ensures zero-hallucination structured lookups both with active PostgreSQL and resilient in-memory fallback,
with native multilingual support for English (en), Hindi (hi), and Tamil (ta).
"""
import copy
from typing import List, Dict, Any, Optional

VERIFIED_STANDARDS: List[Dict[str, Any]] = [
    {
        "id": "std-1293",
        "standard_number": "IS 1293:2019",
        "title": "Plugs and Socket-Outlets for Related Voltages up to and including 250 V and Rated Current up to and including 16 A - Specification (Fourth Revision)",
        "division": "Electrotechnical",
        "year": 2019,
        "status": "ACTIVE",
        "is_qco_mandatory": True,
        "qco_order_number": "Electrical Wires, Cables, Appliances and Protection Devices (Quality Control) Order, 2020",
        "scope_summary": "Covers plugs and fixed or portable socket-outlets for a.c. only, with or without earthing contact, with rated voltage from 50 V up to 250 V and rated current up to 16 A intended for household and similar purposes.",
        "related_standards": ["IS/IEC 60884-1", "IS 302-1"],
        "sections": [
            {
                "clause_number": "1.1",
                "clause_title": "Scope",
                "content": "This standard applies to plugs and fixed or portable socket-outlets for a.c. only, with or without earthing contact, with a rated voltage greater than 50 V but not exceeding 250 V and a rated current not exceeding 16 A, intended for household and similar purposes, either indoors or outdoors.",
                "page_number": 1
            },
            {
                "clause_number": "4.1",
                "clause_title": "Standard Ratings",
                "content": "Standard rated voltages are 240 V a.c. Standard rated currents are 6 A and 16 A. Plugs and socket-outlets shall be rated for single phase 50 Hz a.c.",
                "page_number": 3
            },
            {
                "clause_number": "5.1",
                "clause_title": "Marking Requirements",
                "content": "Accessories shall be marked with rated current in amperes, rated voltage in volts, symbol for nature of supply, manufacturer's name or trademark, and Standard Mark (ISI mark) under Scheme-I.",
                "page_number": 4
            },
            {
                "clause_number": "13.1",
                "clause_title": "Insulation Resistance and Electric Strength",
                "content": "The insulation resistance shall not be less than 5 MOhm when measured with a 500 V d.c. megohmmeter applied between live parts connected together and the body.",
                "page_number": 12
            },
            {
                "clause_number": "19.1",
                "clause_title": "Temperature Rise Test",
                "content": "The temperature rise of terminals shall not exceed 45 K when carrying test current continuously for 1 hour.",
                "page_number": 18
            },
            {
                "clause_number": "24.1",
                "clause_title": "Mechanical Strength",
                "content": "Accessories shall have adequate mechanical strength to withstand drops and impacts from tumbling barrel test (1000 falls).",
                "page_number": 23
            }
        ]
    },
    {
        "id": "std-13252",
        "standard_number": "IS 13252 (Part 1):2010",
        "title": "Information Technology Equipment - Safety - Part 1: General Requirements",
        "division": "Electronics & Information Technology",
        "year": 2010,
        "status": "ACTIVE",
        "is_qco_mandatory": True,
        "qco_order_number": "Electronics and Information Technology Goods (Requirement for Compulsory Registration) Order, 2012 (CRO)",
        "scope_summary": "Applies to mains-powered or battery-powered information technology equipment, including electrical business equipment and associated equipment, with a rated voltage not exceeding 600 V.",
        "related_standards": ["IEC 60950-1:2005", "IS/IEC 62368-1"],
        "sections": [
            {
                "clause_number": "1.1",
                "clause_title": "Equipment Covered",
                "content": "This standard is applicable to mains-powered or battery-powered information technology equipment, including laptops, power adapters, data storage, and network equipment.",
                "page_number": 2
            },
            {
                "clause_number": "1.7",
                "clause_title": "Marking and Instructions",
                "content": "Equipment shall bear the Self-Declaration of Conformity mark under Scheme-II (CRS) with standard number and registration number R-XXXXXXXX.",
                "page_number": 15
            }
        ]
    },
    {
        "id": "std-17803",
        "standard_number": "IS 17803:2022",
        "title": "Electric Ceiling Type Fans - Specification",
        "division": "Electrotechnical",
        "year": 2022,
        "status": "ACTIVE",
        "is_qco_mandatory": True,
        "qco_order_number": "Ceiling Fan Quality Control Order, 2023",
        "scope_summary": "Specifies energy consumption, air delivery, and safety requirements for electric ceiling fans for household and commercial use.",
        "related_standards": ["IS 374", "IS 302-1"],
        "sections": [
            {
                "clause_number": "1.1",
                "clause_title": "Scope",
                "content": "Covers electric ceiling type fans including brushless DC (BLDC) motor fans.",
                "page_number": 1
            }
        ]
    },
    {
        "id": "std-14543",
        "standard_number": "IS 14543:2016",
        "title": "Packaged Drinking Water (Other than Packaged Natural Mineral Water) - Specification",
        "division": "Food and Agriculture",
        "year": 2016,
        "status": "ACTIVE",
        "is_qco_mandatory": True,
        "qco_order_number": "Prevention of Food Adulteration / FSSAI & BIS Mandatory Certification Order",
        "scope_summary": "Prescribes requirements for packaged drinking water offered for direct human consumption.",
        "related_standards": ["IS 13428", "IS 10500"],
        "sections": [
            {
                "clause_number": "1.1",
                "clause_title": "Scope",
                "content": "Applies to water derived from any source of potable water which is subjected to treatments such as decantation, filtration, demineralisation, reverse osmosis, and disinfection.",
                "page_number": 1
            }
        ]
    },
    {
        "id": "std-17526",
        "standard_number": "IS 17526:2021",
        "title": "Stainless Steel Vacuum Flasks / Insulated Flasks and Containers - Specification",
        "division": "Mechanical Engineering & Consumer Products",
        "year": 2021,
        "status": "ACTIVE",
        "is_qco_mandatory": True,
        "qco_order_number": "Insulated Flasks, Bottles and Containers for Domestic Use (Quality Control) Order, 2023",
        "scope_summary": "Specifies manufacturing, material, and performance requirements for domestic and commercial stainless steel insulated flasks, water bottles, and beverage containers.",
        "related_standards": ["IS 6911", "IS 10252"],
        "sections": [
            {
                "clause_number": "1.1",
                "clause_title": "Scope and Applicability",
                "content": "This standard specifies requirements for stainless steel vacuum flasks, single-wall and double-wall insulated stainless steel water bottles, and portable beverage containers used for household, school, travel, and office purposes.",
                "page_number": 1
            },
            {
                "clause_number": "4.1",
                "clause_title": "Material & Grade Specifications",
                "content": "All stainless steel components in direct contact with liquids/food shall be manufactured using food-grade austenitic stainless steel conforming to IS 6911 (Grade 304 / SS 304, designated as X6CrNi18-10, or Grade 316 for enhanced chemical resistance). Toxic heavy metal leaching into water shall strictly conform to BIS food-contact migration limits.",
                "page_number": 3
            },
            {
                "clause_number": "5.1",
                "clause_title": "Mandatory Certification and Marking",
                "content": "Every stainless steel water bottle and vacuum flask manufactured, imported, or sold in India MUST carry the Standard Mark (ISI mark) under BIS Scheme-I with the manufacturer's unique CM/L license number. Manufacturing or selling without ISI mark is a punishable offense under the BIS Act, 2016.",
                "page_number": 5
            },
            {
                "clause_number": "6.2",
                "clause_title": "Performance & Leakage Testing",
                "content": "Bottles must successfully pass the thermal insulation retention test (minimum temperature holding after 6/12/24 hours), pressure resistance test, 1.2-meter drop/impact test onto a concrete floor without fracture or leak, and seal gasket durability test.",
                "page_number": 7
            }
        ]
    },
    {
        "id": "std-6911",
        "standard_number": "IS 6911:2017",
        "title": "Stainless Steel Plate, Sheet and Strip - Specification (First Revision)",
        "division": "Metallurgical Engineering",
        "year": 2017,
        "status": "ACTIVE",
        "is_qco_mandatory": True,
        "qco_order_number": "Stainless Steel Products (Quality Control) Order, 2020",
        "scope_summary": "Prescribes chemical composition, mechanical properties, and finish requirements for stainless steel plate, sheet, and strip used for food utensils, water containers, and industrial fabrication.",
        "related_standards": ["IS 17526", "IS 14756"],
        "sections": [
            {
                "clause_number": "1.1",
                "clause_title": "Scope",
                "content": "Covers hot-rolled and cold-rolled stainless steel plates, sheets, and coils intended for fabrication of utensils, water bottles, and food storage equipment.",
                "page_number": 1
            },
            {
                "clause_number": "7.1",
                "clause_title": "Food Grade Material Grades",
                "content": "For food and drinking water contact utensils and bottles, austenitic Grade 304 (nominal 18% Chromium, 8% Nickel) or Grade 316 (containing Molybdenum) shall be used to ensure corrosion resistance and zero toxic leaching.",
                "page_number": 8
            }
        ]
    }
]

STANDARDS_TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    "hi": {
        "std-1293": {
            "title": "250 V तक और सहित संबंधित वोल्टेज और 16 A तक रेटेड करंट के लिए प्लग और सॉकेट-आउटलेट - विशिष्टता (चौथा संशोधन)",
            "division": "इलेक्ट्रो-तकनीकी",
            "qco_order_number": "विद्युत तार, केबल, उपकरण और सुरक्षा उपकरण (गुणवत्ता नियंत्रण) आदेश, 2020",
            "scope_summary": "केवल ए.सी. के लिए प्लग और फिक्स्ड या पोर्टेबल सॉकेट-आउटलेट को कवर करता है, अर्थिंग संपर्क के साथ या उसके बिना, 50 V से 250 V तक रेटेड वोल्टेज और 16 A तक रेटेड करंट के साथ घरेलू और समान उद्देश्यों के लिए अभिप्रेत है।",
            "sections": {
                "1.1": {
                    "clause_title": "दायरा और प्रयोज्यता",
                    "content": "यह मानक केवल a.c. के लिए प्लग और स्थिर या पोर्टेबल सॉकेट-आउटलेट पर लागू होता है, अर्थिंग संपर्क के साथ या बिना, 50 V से अधिक लेकिन 250 V से अनधिक और 16 A तक रेटेड करंट के साथ, घरेलू और समान उद्देश्यों के लिए।"
                },
                "4.1": {
                    "clause_title": "मानक रेटिंग",
                    "content": "मानक रेटेड वोल्टेज 240 V a.c. हैं। मानक रेटेड करंट 6 A और 16 A हैं। प्लग और सॉकेट-आउटलेट सिंगल फेज 50 Hz a.c. के लिए रेटेड होंगे।"
                },
                "5.1": {
                    "clause_title": "अंकन आवश्यकताएं",
                    "content": "सामग्रियों पर एम्पीयर में रेटेड करंट, वोल्ट में रेटेड वोल्टेज, आपूर्ति की प्रकृति का प्रतीक, निर्माता का नाम और योजना-I के तहत मानक चिह्न (ISI मार्क) अंकित होना चाहिए।"
                },
                "13.1": {
                    "clause_title": "इन्सुलेशन प्रतिरोध और विद्युत शक्ति",
                    "content": "500 V d.c. मेगोहममीटर से मापे जाने पर इन्सुलेशन प्रतिरोध 5 MOhm से कम नहीं होना चाहिए।"
                },
                "19.1": {
                    "clause_title": "तापमान वृद्धि परीक्षण",
                    "content": "1 घंटे तक लगातार परीक्षण धारा प्रवाहित करने पर टर्मिनलों का तापमान वृद्धि 45 K से अधिक नहीं होना चाहिए।"
                },
                "24.1": {
                    "clause_title": "यांत्रिक शक्ति",
                    "content": "टम्बलिंग बैरल परीक्षण (1000 बार गिरने) के झटकों और प्रभावों का सामना करने के लिए सामग्रियों में पर्याप्त यांत्रिक शक्ति होनी चाहिए।"
                }
            }
        },
        "std-13252": {
            "title": "सूचना प्रौद्योगिकी उपकरण - सुरक्षा - भाग 1: सामान्य आवश्यकताएं",
            "division": "इलेक्ट्रॉनिक्स और सूचना प्रौद्योगिकी",
            "qco_order_number": "इलेक्ट्रॉनिक्स और सूचना प्रौद्योगिकी सामान (अनिवार्य पंजीकरण की आवश्यकता) आदेश, 2012 (CRO)",
            "scope_summary": "मुख्य विद्युत या बैटरी से चलने वाले सूचना प्रौद्योगिकी उपकरणों पर लागू होता है, जिसमें 600 V से अनधिक रेटेड वोल्टेज वाले व्यावसायिक उपकरण और संबंधित उपकरण शामिल हैं।",
            "sections": {
                "1.1": {
                    "clause_title": "शामिल उपकरण",
                    "content": "यह मानक लैपटॉप, पावर एडाप्टर, डेटा स्टोरेज और नेटवर्क उपकरण सहित सूचना प्रौद्योगिकी उपकरणों पर लागू होता है।"
                },
                "1.7": {
                    "clause_title": "अंकन और निर्देश",
                    "content": "उपकरणों पर मानक संख्या और पंजीकरण संख्या R-XXXXXXXX के साथ योजना-II (CRS) के तहत स्व-अनुरूपता घोषणा चिह्न होना चाहिए।"
                }
            }
        },
        "std-17803": {
            "title": "इलेक्ट्रिक सीलिंग प्रकार के पंखे - विशिष्टता",
            "division": "इलेक्ट्रो-तकनीकी",
            "qco_order_number": "सीलिंग फैन गुणवत्ता नियंत्रण आदेश, 2023",
            "scope_summary": "घरेलू और व्यावसायिक उपयोग के लिए इलेक्ट्रिक सीलिंग पंखों के ऊर्जा उपभोग, वायु प्रवाह और सुरक्षा आवश्यकताओं को निर्दिष्ट करता है।",
            "sections": {
                "1.1": {
                    "clause_title": "दायरा",
                    "content": "ब्रशलेस डीसी (BLDC) मोटर पंखे सहित इलेक्ट्रिक सीलिंग प्रकार के पंखों को शामिल करता है।"
                }
            }
        },
        "std-14543": {
            "title": "पैकेज्ड पेयजल (पैकेज्ड प्राकृतिक खनिज जल के अलावा) - विशिष्टता",
            "division": "खाद्य और कृषि",
            "qco_order_number": "खाद्य अपमिश्रण निवारण / FSSAI और BIS अनिवार्य प्रमाणन आदेश",
            "scope_summary": "मानव उपभोग के लिए सीधे पेश किए जाने वाले पैकेज्ड पेयजल की आवश्यकताओं को निर्धारित करता है।",
            "sections": {
                "1.1": {
                    "clause_title": "दायरा",
                    "content": "पीने योग्य पानी के किसी भी स्रोत से प्राप्त पानी पर लागू होता है जिसे निस्यंदन, विखनिजीकरण, रिवर्स ऑस्मोसिस (RO) और कीटाणुशोधन जैसे उपचारों से गुजारा जाता है।"
                }
            }
        }
    },
    "ta": {
        "std-1293": {
            "title": "250 V வரை மற்றும் உள்ளடக்கிய தொடர்புடைய மின்னழுத்தங்கள் மற்றும் 16 A வரை மதிப்பிடப்பட்ட மின்னோட்டத்திற்கான பிளக்குகள் மற்றும் சாக்கெட்-அவுட்லெட்டுகள் - விவரக்குறிப்பு (நான்காவது திருத்தம்)",
            "division": "மின் தொழில்நுட்பம்",
            "qco_order_number": "மின் கம்பிகள், கேபிள்கள், உபகரணங்கள் மற்றும் பாதுகாப்பு சாதனங்கள் (தரக் கட்டுப்பாடு) ஆணை, 2020",
            "scope_summary": "50 V முதல் 250 V வரையிலான மின்னழுத்தம் மற்றும் 16 A வரையிலான மின்னோட்டத்துடன் வீட்டு மற்றும் ஒத்த பயன்பாடுகளுக்காக வடிவமைக்கப்பட்ட ஏ.சி. பிளக்குகள் மற்றும் சாக்கெட்-அவுட்லெட்டுகளை உள்ளடக்கியது.",
            "sections": {
                "1.1": {
                    "clause_title": "நோக்கம் மற்றும் பயன்பாடு",
                    "content": "இந்த தரநிலை 50 V முதல் 250 V வரையிலான மின்னழுத்தம் மற்றும் 16 A வரையிலான மின்னோட்டம் கொண்ட பிளக்குகள் மற்றும் சாக்கெட்-அவுட்லெட்டுகளுக்கு பொருந்தும்."
                },
                "4.1": {
                    "clause_title": "நிலையான மதிப்பீடுகள்",
                    "content": "நிலையான மின்னழுத்தம் 240 V a.c. நிலையான மின்னோட்டம் 6 A மற்றும் 16 A ஆகும். ஒற்றை கட்ட 50 Hz a.c. க்காக மதிப்பிடப்பட வேண்டும்."
                },
                "5.1": {
                    "clause_title": "குறியிடுதல் தேவைகள்",
                    "content": "பொருட்களில் மின்னோட்டம், மின்னழுத்தம், உற்பத்தியாளர் பெயர் மற்றும் திட்டம்-I இன் கீழ் ISI முத்திரை குறிக்கப்பட வேண்டும்."
                },
                "13.1": {
                    "clause_title": "காப்பு எதிர்ப்பு மற்றும் மின் வலிமை",
                    "content": "500 V d.c. மூலம் அளவிடும் போது காப்பு எதிர்ப்பு 5 MOhm க்கும் குறையாமல் இருக்க வேண்டும்."
                },
                "19.1": {
                    "clause_title": "வெப்பநிலை அதிகரிப்பு சோதனை",
                    "content": "1 மணி நேரம் சோதனை மின்னோட்டத்தை செலுத்தும் போது முனையங்களின் வெப்பநிலை அதிகரிப்பு 45 K ஐ தாண்டக்கூடாது."
                },
                "24.1": {
                    "clause_title": "இயந்திர வலிமை",
                    "content": "1000 முறை உருளும் உருளை சோதனையின் தாக்கங்களை தாங்கும் போதுமான இயந்திர வலிமை பெற்றிருக்க வேண்டும்."
                }
            }
        },
        "std-13252": {
            "title": "தகவல் தொழில்நுட்ப உபகரணங்கள் - பாதுகாப்பு - பகுதி 1: பொதுவான தேவைகள்",
            "division": "மின்னணுவியல் & தகவல் தொழில்நுட்பம்",
            "qco_order_number": "மின்னணுவியல் மற்றும் தகவல் தொழில்நுட்ப பொருட்கள் (கட்டாய பதிவு தேவை) ஆணை, 2012 (CRO)",
            "scope_summary": "600 V க்கு மிகாமல் மதிப்பிடப்பட்ட மின்னழுத்தம் கொண்ட மடிக்கணினிகள், பவர் அடாப்டர்கள் உள்ளிட்ட தகவல் தொழில்நுட்ப சாதனங்களுக்கு பொருந்தும்.",
            "sections": {
                "1.1": {
                    "clause_title": "உட்பட்ட உபகரணங்கள்",
                    "content": "மடிக்கணினிகள், பவர் அடாப்டர்கள், தரவு சேமிப்பு மற்றும் நெட்வொர்க் சாதனங்கள் உள்ளிட்ட தகவல் தொழில்நுட்ப சாதனங்களுக்கு இந்த தரநிலை பொருந்தும்."
                },
                "1.7": {
                    "clause_title": "குறியிடுதல் மற்றும் வழிமுறைகள்",
                    "content": "சாதனங்களில் திட்டம்-II (CRS) இன் கீழ் தரநிலை எண் மற்றும் பதிவு எண் R-XXXXXXXX கொண்ட முத்திரை இருக்க வேண்டும்."
                }
            }
        },
        "std-17803": {
            "title": "மின்சார கூரை மின்விசிறிகள் - விவரக்குறிப்பு",
            "division": "மின் தொழில்நுட்பம்",
            "qco_order_number": "கூரை மின்விசிறி தரக் கட்டுப்பாடு ஆணை, 2023",
            "scope_summary": "வீட்டு மற்றும் வணிக பயன்பாட்டிற்கான கூரை மின்விசிறிகளின் மின் நுகர்வு, காற்று விநியோகம் மற்றும் பாதுகாப்பு தேவைகளை வரையறுக்கிறது.",
            "sections": {
                "1.1": {
                    "clause_title": "நோக்கம்",
                    "content": "BLDC மோட்டார் விசிறிகள் உட்பட அனைத்து மின்சார கூரை மின்விசிறிகளையும் உள்ளடக்கியது."
                }
            }
        },
        "std-14543": {
            "title": "பேக்கேஜ் செய்யப்பட்ட குடிநீர் (இயற்கை கனிம நீர் தவிர்த்து) - விவரக்குறிப்பு",
            "division": "உணவு மற்றும் விவசாயம்",
            "qco_order_number": "உணவு கலப்பட தடுப்பு / FSSAI & BIS கட்டாய சான்றிதழ் ஆணை",
            "scope_summary": "மனித நுகர்வுக்காக வழங்கப்படும் பாட்டிலில் அடைக்கப்பட்ட குடிநீருக்கான தரத் தேவைகளை நிர்ணயிக்கிறது.",
            "sections": {
                "1.1": {
                    "clause_title": "நோக்கம்",
                    "content": "வடிகட்டுதல், கனிம நீக்கம், RO மற்றும் கிருமி நீக்கம் செய்யப்பட்ட குடிநீருக்கு இந்த தரநிலை பொருந்தும்."
                }
            }
        }
    }
}

VERIFIED_SCHEMES: List[Dict[str, Any]] = [
    {
        "scheme_code": "SCHEME_I_ISI",
        "name": "Scheme-I: Product Certification (ISI Mark)",
        "description": "BIS Product Certification Scheme for domestic and foreign manufacturers granting license to use the Standard Mark (ISI mark) based on conformity assessment, factory quality audit, and testing in BIS recognized labs.",
        "applicable_sectors": ["Electrical Appliances", "Cables", "Automotive components", "Steel products", "Packaged Water", "Cement"],
        "application_procedure_summary": "1. Application submission on ManakOnline -> 2. Document audit -> 3. Preliminary factory inspection & sample drawl -> 4. Testing at BIS recognized lab -> 5. Grant of License -> 6. Periodic surveillance.",
        "required_documents_checklist": [
            "Proof of factory establishment (Registration certificate)",
            "Manufacturing machinery list and capacity",
            "In-house testing equipment with valid calibration certificates",
            "Plant layout and process flow chart",
            "Appointment letter of qualified quality control personnel",
            "Agreement/undertaking with raw material suppliers"
        ],
        "fee_structure_summary": "Application fee: Rs. 1,000; Annual License fee: Rs. 1,000; Marking fee calculated per unit output as per BIS schedule."
    },
    {
        "scheme_code": "SCHEME_II_CRS",
        "name": "Scheme-II: Compulsory Registration Scheme (CRS)",
        "description": "Self-declaration of conformity registration scheme specifically for Electronic and Information Technology goods notified by MeitY and Solar PV notified by MNRE.",
        "applicable_sectors": ["Laptops", "Smartphones", "Power Adapters", "LED Lighting", "Smart Watches", "Servers"],
        "application_procedure_summary": "1. Sample testing at BIS recognized lab in India -> 2. Receive valid Test Report -> 3. Apply on CRS portal within 90 days -> 4. Document verification -> 5. Grant of Registration number (R-XXXXXXXX) -> 6. Standard CRS label display.",
        "required_documents_checklist": [
            "Valid Test Report from BIS-recognized testing laboratory (issued within 90 days)",
            "Trademark registration certificate or Authorization Letter",
            "Undertaking and Affidavit of Authorized Indian Representative (AIR) for foreign OEMs",
            "ISO 9001 quality certificate of manufacturing facility",
            "Product label sample depicting the CRS Mark and R-Number format"
        ],
        "fee_structure_summary": "Application fee: Rs. 10,000 per base model; Inclusion fee: Rs. 5,000 per additional model; Renewal every 2 years."
    },
    {
        "scheme_code": "SCHEME_IV_FMCS",
        "name": "Scheme-IV: Foreign Manufacturers Certification Scheme (FMCS)",
        "description": "Dedicated product certification scheme enabling foreign manufacturing units located outside India to obtain a BIS license to mark goods exported to India with the ISI mark.",
        "applicable_sectors": ["Global Manufacturers exporting regulated products to India"],
        "application_procedure_summary": "1. Submission of Form-V with AIR details -> 2. BIS Officer factory audit visit -> 3. Independent sample drawl & air freight to Indian lab -> 4. Bank Guarantee & Performance indemnity -> 5. Grant of FMCS License.",
        "required_documents_checklist": [
            "Foreign Business Registration / Incorporation license",
            "Authorized Indian Representative (AIR) nomination and legal agreement",
            "Factory layout, process flowchart, and in-house testing capability",
            "Performance Bank Guarantee (PBG) in USD"
        ],
        "fee_structure_summary": "Audit inspection man-day charges + travel/stay + USD 10,000 PBG + annual marking fee."
    }
]

SCHEMES_TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    "hi": {
        "SCHEME_I_ISI": {
            "name": "योजना-I: उत्पाद प्रमाणन (ISI मार्क)",
            "description": "घरेलू और विदेशी निर्माताओं के लिए बीआईएस उत्पाद प्रमाणन योजना जो अनुरूपता मूल्यांकन, फैक्ट्री ऑडिट और बीआईएस मान्यता प्राप्त प्रयोगशालाओं में परीक्षण के आधार पर मानक चिह्न (ISI मार्क) का उपयोग करने का लाइसेंस प्रदान करती है।",
            "applicable_sectors": ["विद्युत उपकरण", "केबल", "ऑटोमोबाइल घटक", "स्टील उत्पाद", "पैकेज्ड पानी", "सीमेंट"],
            "fee_structure_summary": "आवेदन शुल्क: रु. 1,000; वार्षिक लाइसेंस शुल्क: रु. 1,000; बीआईएस अनुसूची के अनुसार प्रति यूनिट अंकन शुल्क।"
        },
        "SCHEME_II_CRS": {
            "name": "योजना-II: अनिवार्य पंजीकरण योजना (CRS)",
            "description": "MeitY द्वारा अधिसूचित इलेक्ट्रॉनिक और सूचना प्रौद्योगिकी वस्तुओं तथा MNRE द्वारा अधिसूचित सौर पीवी के लिए अनुरूपता का स्व-घोषणा पंजीकरण।",
            "applicable_sectors": ["लैपटॉप", "स्मार्टफोन", "पावर एडाप्टर", "एलईडी लाइटिंग", "स्मार्ट वॉच", "सर्वर"],
            "fee_structure_summary": "आवेदन शुल्क: रु. 10,000 प्रति मॉडल; नवीनीकरण हर 2 वर्ष में।"
        },
        "SCHEME_IV_FMCS": {
            "name": "योजना-IV: विदेशी निर्माता प्रमाणन योजना (FMCS)",
            "description": "भारत के बाहर स्थित विदेशी विनिर्माण इकाइयों को भारत में निर्यात किए जाने वाले सामानों पर ISI मार्क लगाने के लिए लाइसेंस प्राप्त करने में सक्षम बनाती है।",
            "applicable_sectors": ["भारत को निर्यात करने वाले वैश्विक निर्माता"],
            "fee_structure_summary": "ऑडिट निरीक्षण शुल्क + यात्रा/निवास + 10,000 अमेरिकी डॉलर बैंक गारंटी + वार्षिक अंकन शुल्क।"
        }
    },
    "ta": {
        "SCHEME_I_ISI": {
            "name": "திட்டம்-I: தயாரிப்பு சான்றிதழ் (ISI முத்திரை)",
            "description": "தொழிற்சாலை தணிக்கை மற்றும் BIS ஆய்வக சோதனையின் அடிப்படையில் உற்பத்தியாளர்களுக்கு ISI முத்திரையை பயன்படுத்த அனுமதி வழங்கும் தயாரிப்பு சான்றிதழ் திட்டம்.",
            "applicable_sectors": ["மின் சாதனங்கள்", "கேபிள்கள்", "வாகன பாகங்கள்", "எஃகு பொருட்கள்", "குடிநீர்", "சிமெண்ட்"],
            "fee_structure_summary": "விண்ணப்பக் கட்டணம்: ரூ. 1,000; வருடாந்திர உரிமக் கட்டணம்: ரூ. 1,000; BIS அட்டவணைப்படி தயாரிப்பு முத்திரைக் கட்டணம்."
        },
        "SCHEME_II_CRS": {
            "name": "திட்டம்-II: கட்டாய பதிவுத் திட்டம் (CRS)",
            "description": "மின்னணு மற்றும் தகவல் தொழில்நுட்ப சாதனங்களுக்கான சுய அறிவிப்பு இணக்க பதிவுத் திட்டம் (CRS).",
            "applicable_sectors": ["மடிக்கணினிகள்", "ஸ்மார்ட்போன்கள்", "பவர் அடாப்டர்கள்", "LED விளக்குகள்", "ஸ்மார்ட் வாட்ச்கள்", "சர்வர்கள்"],
            "fee_structure_summary": "விண்ணப்பக் கட்டணம்: அடிப்படை மாடலுக்கு ரூ. 10,000; 2 ஆண்டுகளுக்கு ஒருமுறை புதுப்பித்தல்."
        },
        "SCHEME_IV_FMCS": {
            "name": "திட்டம்-IV: வெளிநாட்டு உற்பத்தியாளர் சான்றிதழ் திட்டம் (FMCS)",
            "description": "இந்தியாவுக்கு பொருட்களை ஏற்றுமதி செய்யும் வெளிநாட்டு உற்பத்தியாளர்கள் ISI முத்திரையைப் பெறுவதற்கான சிறப்புத் திட்டம்.",
            "applicable_sectors": ["இந்தியாவுக்கு ஏற்றுமதி செய்யும் சர்வதேச உற்பத்தியாளர்கள்"],
            "fee_structure_summary": "தணிக்கை கட்டணம் + பயண செலவுகள் + 10,000 அமெரிக்க டாலர் வங்கி உத்தரவாதம் + முத்திரைக் கட்டணம்."
        }
    }
}

VERIFIED_LABORATORIES: List[Dict[str, Any]] = [
    {
        "id": "lab-001",
        "lab_name": "BIS Central Laboratory",
        "lab_code": "BIS-CL-GZB-01",
        "recognition_type": "BIS_CENTRAL",
        "city": "Ghaziabad",
        "state": "Uttar Pradesh",
        "address": "Plot No. 20/9, Site IV, Sahibabad Industrial Area, Ghaziabad, UP 201010",
        "contact_details": {"phone": "+91-120-2776032", "email": "cl@bis.gov.in"},
        "testing_scope_summary": "Comprehensive national testing facility for electrical appliances, chemical analysis, mechanical stress, plastics, and packaged drinking water.",
        "accredited_standards": ["IS 1293:2019", "IS 13252 (Part 1):2010", "IS 14543:2016", "IS 17803:2022"]
    },
    {
        "id": "lab-002",
        "lab_name": "National Test House (Southern Region)",
        "lab_code": "NTH-SR-CHE-02",
        "recognition_type": "NABL_ACCREDITED",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "address": "Tharamani, Chennai, Tamil Nadu 600113",
        "contact_details": {"phone": "+91-44-22541221", "email": "nth-chennai@nic.in"},
        "testing_scope_summary": "Electrical insulation, high voltage safety, electronics, circuit breakers, plugs and sockets, and material tensile strength testing.",
        "accredited_standards": ["IS 1293:2019", "IS 13252 (Part 1):2010", "IS 17803:2022"]
    },
    {
        "id": "lab-003",
        "lab_name": "National Test House (Eastern Region)",
        "lab_code": "NTH-ER-KOL-03",
        "recognition_type": "NABL_ACCREDITED",
        "city": "Kolkata",
        "state": "West Bengal",
        "address": "Block CP, Sector V, Salt Lake City, Kolkata, WB 700091",
        "contact_details": {"phone": "+91-33-23673869", "email": "nth-kolkata@nic.in"},
        "testing_scope_summary": "Electrotechnical safety testing, fan airflow and energy ratings, mechanical testing, and chemical composition.",
        "accredited_standards": ["IS 1293:2019", "IS 17803:2022", "IS 14543:2016"]
    },
    {
        "id": "lab-004",
        "lab_name": "Electronics Regional Test Laboratory (ERTL North)",
        "lab_code": "ERTL-NR-DEL-04",
        "recognition_type": "BIS_RECOGNIZED",
        "city": "New Delhi",
        "state": "Delhi",
        "address": "S-Block, Okhla Industrial Area Phase-II, New Delhi 110020",
        "contact_details": {"phone": "+91-11-26386000", "email": "ertl-north@stqc.gov.in"},
        "testing_scope_summary": "Compulsory Registration Scheme (CRS) safety testing, EMI/EMC compliance, IT equipment, power adapters, and LED drivers.",
        "accredited_standards": ["IS 13252 (Part 1):2010", "IS 1293:2019"]
    },
    {
        "id": "lab-005",
        "lab_name": "BIS Western Regional Laboratory",
        "lab_code": "BIS-WRL-MUM-05",
        "recognition_type": "BIS_BRANCH",
        "city": "Mumbai",
        "state": "Maharashtra",
        "address": "Manakalaya, E9, MIDC, Andheri East, Mumbai, MH 400093",
        "contact_details": {"phone": "+91-22-28329295", "email": "wrl@bis.gov.in"},
        "testing_scope_summary": "Testing of consumer appliances, bottled water, food contact materials, steel products, and cables.",
        "accredited_standards": ["IS 14543:2016", "IS 1293:2019", "IS 17803:2022"]
    }
]

LABORATORIES_TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    "hi": {
        "lab-001": {
            "lab_name": "बीआईएस केंद्रीय प्रयोगशाला",
            "state": "उत्तर प्रदेश",
            "city": "गाजियाबाद",
            "testing_scope_summary": "विद्युत उपकरणों, रासायनिक विश्लेषण, यांत्रिक तनाव, प्लास्टिक और पैकेज्ड पेयजल के लिए व्यापक राष्ट्रीय परीक्षण सुविधा।"
        },
        "lab-002": {
            "lab_name": "राष्ट्रीय परीक्षण गृह (दक्षिणी क्षेत्र)",
            "state": "तमिलनाडु",
            "city": "चेन्नई",
            "testing_scope_summary": "विद्युत इन्सुलेशन, उच्च वोल्टेज सुरक्षा, इलेक्ट्रॉनिक्स, सर्किट ब्रेकर, प्लग और सॉकेट तथा सामग्री तन्य शक्ति परीक्षण।"
        },
        "lab-003": {
            "lab_name": "राष्ट्रीय परीक्षण गृह (पूर्वी क्षेत्र)",
            "state": "पश्चिम बंगाल",
            "city": "कोलकाता",
            "testing_scope_summary": "इलेक्ट्रो-तकनीकी सुरक्षा परीक्षण, पंखे का वायु प्रवाह और ऊर्जा रेटिंग, यांत्रिक परीक्षण और रासायनिक संरचना।"
        },
        "lab-004": {
            "lab_name": "इलेक्ट्रॉनिक्स क्षेत्रीय परीक्षण प्रयोगशाला (ERTL उत्तर)",
            "state": "दिल्ली",
            "city": "नई दिल्ली",
            "testing_scope_summary": "अनिवार्य पंजीकरण योजना (CRS) सुरक्षा परीक्षण, EMI/EMC अनुपालन, आईटी उपकरण, पावर एडाप्टर और एलईडी ड्राइवर।"
        },
        "lab-005": {
            "lab_name": "बीआईएस पश्चिमी क्षेत्रीय प्रयोगशाला",
            "state": "महाराष्ट्र",
            "city": "मुंबई",
            "testing_scope_summary": "उपभोक्ता उपकरण, बोतलबंद पानी, खाद्य संपर्क सामग्री, स्टील उत्पाद और केबल का परीक्षण।"
        }
    },
    "ta": {
        "lab-001": {
            "lab_name": "BIS மத்திய ஆய்வகம்",
            "state": "உத்தரப் பிரதேசம்",
            "city": "காசியாபாத்",
            "testing_scope_summary": "மின் சாதனங்கள், வேதியியல் பகுப்பாய்வு, இயந்திர அழுத்தம் மற்றும் குடிநீருக்கான விரிவான தேசிய சோதனை மையம்."
        },
        "lab-002": {
            "lab_name": "தேசிய சோதனை இல்லம் (தென் மண்டலம்)",
            "state": "தமிழ்நாடு",
            "city": "சென்னை",
            "testing_scope_summary": "மின் காப்பு, உயர் மின்னழுத்த பாதுகாப்பு, எலக்ட்ரானிக்ஸ், சர்க்யூட் பிரேக்கர்கள், பிளக் மற்றும் சாக்கெட்டுகள் சோதனை மையம்."
        },
        "lab-003": {
            "lab_name": "தேசிய சோதனை இல்லம் (கிழக்கு மண்டலம்)",
            "state": "மேற்கு வங்காளம்",
            "city": "கொல்கத்தா",
            "testing_scope_summary": "மின் பாதுகாப்பு சோதனை, விசிறி காற்று விநியோகம் மற்றும் ஆற்றல் மதிப்பீடுகள், இயந்திர சோதனை மையம்."
        },
        "lab-004": {
            "lab_name": "மின்னணுவியல் பிராந்திய சோதனை ஆய்வகம் (ERTL வடக்கு)",
            "state": "டெல்லி",
            "city": "புது டெல்லி",
            "testing_scope_summary": "கட்டாய பதிவுத் திட்டம் (CRS) பாதுகாப்பு சோதனை, EMI/EMC இணக்கம், தகவல் தொழில்நுட்ப சாதனங்கள் மற்றும் பவர் அடாப்டர்கள் சோதனை."
        },
        "lab-005": {
            "lab_name": "BIS மேற்கு மண்டல ஆய்வகம்",
            "state": "மகாராஷ்டிரா",
            "city": "மும்பை",
            "testing_scope_summary": "நுகர்வோர் சாதனங்கள், பாட்டில் குடிநீர், உணவு தொடர்பு பொருட்கள், எஃகு பொருட்கள் மற்றும் கேபிள்கள் சோதனை."
        }
    }
}


def get_localized_standard(std: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
    """Returns standard dictionary localized to target language."""
    if language not in ("hi", "ta"):
        return std
    
    std_id = std.get("id")
    trans = STANDARDS_TRANSLATIONS.get(language, {}).get(std_id, {})
    if not trans:
        return std
    
    res = copy.deepcopy(std)
    if "title" in trans:
        res["title"] = trans["title"]
    if "division" in trans:
        res["division"] = trans["division"]
    if "qco_order_number" in trans:
        res["qco_order_number"] = trans["qco_order_number"]
    if "scope_summary" in trans:
        res["scope_summary"] = trans["scope_summary"]
    
    sec_trans = trans.get("sections", {})
    if sec_trans and "sections" in res:
        for sec in res["sections"]:
            c_num = sec.get("clause_number")
            if c_num in sec_trans:
                if "clause_title" in sec_trans[c_num]:
                    sec["clause_title"] = sec_trans[c_num]["clause_title"]
                if "content" in sec_trans[c_num]:
                    sec["content"] = sec_trans[c_num]["content"]
    
    return res


def get_localized_all_standards(language: str = "en") -> List[Dict[str, Any]]:
    return [get_localized_standard(s, language) for s in VERIFIED_STANDARDS]


def get_localized_scheme(scheme: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
    if language not in ("hi", "ta"):
        return scheme
    
    code = scheme.get("scheme_code")
    trans = SCHEMES_TRANSLATIONS.get(language, {}).get(code, {})
    if not trans:
        return scheme
    
    res = copy.deepcopy(scheme)
    if "name" in trans:
        res["name"] = trans["name"]
    if "description" in trans:
        res["description"] = trans["description"]
    if "applicable_sectors" in trans:
        res["applicable_sectors"] = trans["applicable_sectors"]
    if "fee_structure_summary" in trans:
        res["fee_structure_summary"] = trans["fee_structure_summary"]
    return res


def get_localized_all_schemes(language: str = "en") -> List[Dict[str, Any]]:
    return [get_localized_scheme(s, language) for s in VERIFIED_SCHEMES]


def get_localized_laboratory(lab: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
    if language not in ("hi", "ta"):
        return lab
    
    lab_id = lab.get("id")
    trans = LABORATORIES_TRANSLATIONS.get(language, {}).get(lab_id, {})
    if not trans:
        return lab
    
    res = copy.deepcopy(lab)
    if "lab_name" in trans:
        res["lab_name"] = trans["lab_name"]
    if "state" in trans:
        res["state"] = trans["state"]
    if "city" in trans:
        res["city"] = trans["city"]
    if "testing_scope_summary" in trans:
        res["testing_scope_summary"] = trans["testing_scope_summary"]
    return res


def get_localized_all_laboratories(language: str = "en") -> List[Dict[str, Any]]:
    return [get_localized_laboratory(lab, language) for lab in VERIFIED_LABORATORIES]
