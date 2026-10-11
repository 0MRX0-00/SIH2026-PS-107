"use client";

import React, { useState, useEffect, useCallback, useMemo, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Award,
  CheckCircle2,
  AlertTriangle,
  FileText,
  ArrowRight,
  Sparkles,
  Search,
  Layers,
  FlaskConical,
  BotMessageSquare,
  ShieldCheck,
  Building,
  Info,
  ExternalLink,
  Globe2,
  Factory,
  HelpCircle,
  FileCheck,
  Scale,
  RefreshCw,
  BookOpen,
  ArrowUpRight,
  CheckSquare
} from "lucide-react";
import {
  generateCertificationRoadmap,
  listCertificationSchemes,
  CertificationRoadmapRequest,
  CertificationRoadmapResponse,
  CertificationScheme,
  DocumentChecklistItem,
  OfficialSourceCard
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

interface PresetExample {
  label: string;
  name: string;
  category: string;
  intendedUse: string;
  country: string;
  mfgType: string;
  standard: string;
  labels?: Record<string, string>;
  names?: Record<string, string>;
}

const PRESET_EXAMPLES: PresetExample[] = [
  {
    label: "Electric Ceiling Fans (Scheme-I Normal, Domestic)",
    labels: {
      en: "Electric Ceiling Fans (Scheme-I Normal, Domestic)",
      hi: "इलेक्ट्रिक सीलिंग फैन (योजना-I सामान्य, घरेलू)",
      ta: "மின்சார கூரை மின்விசிறிகள் (திட்டம்-I இயல்பான, உள்நாட்டு)"
    },
    name: "Electric Ceiling Fan",
    names: {
      en: "Electric Ceiling Fan",
      hi: "इलेक्ट्रिक सीलिंग फैन",
      ta: "மின்சார கூரை மின்விசிறி"
    },
    category: "Electrical Equipment & Appliances",
    intendedUse: "Domestic / Household",
    country: "India",
    mfgType: "DOMESTIC_MANUFACTURER",
    standard: "IS 17803:2022"
  },
  {
    label: "Plugs & Socket-Outlets (Scheme-I Normal, Domestic)",
    labels: {
      en: "Plugs & Socket-Outlets (Scheme-I Normal, Domestic)",
      hi: "प्लग और सॉकेट-आउटलेट (योजना-I सामान्य, घरेलू)",
      ta: "பிளக்குகள் மற்றும் சாக்கெட்-அவுட்லெட்டுகள் (திட்டம்-I இயல்பான, உள்நாட்டு)"
    },
    name: "Plugs and Socket-Outlets up to 16A",
    names: {
      en: "Plugs and Socket-Outlets up to 16A",
      hi: "16A तक प्लग और सॉकेट-आउटलेट",
      ta: "16A வரை பிளக்குகள் மற்றும் சாக்கெட்-அவுட்லெட்டுகள்"
    },
    category: "Electrical Equipment & Appliances",
    intendedUse: "Domestic / Household",
    country: "India",
    mfgType: "DOMESTIC_MANUFACTURER",
    standard: "IS 1293:2019"
  },
  {
    label: "Domestic Toys & Appliances (Scheme-I Simplified, 30-day)",
    labels: {
      en: "Domestic Toys & Appliances (Scheme-I Simplified, 30-day)",
      hi: "घरेलू खिलौने एवं उपकरण (योजना-I सरलीकृत, 30 दिन)",
      ta: "உள்நாட்டு பொம்மைகள் மற்றும் உபகரணங்கள் (திட்டம்-I எளிமைப்படுத்தப்பட்டது, 30 நாள்)"
    },
    name: "Children Mechanical & Plastic Toys",
    names: {
      en: "Children Mechanical & Plastic Toys",
      hi: "बच्चों के यांत्रिक एवं प्लास्टिक खिलौने",
      ta: "குழந்தைகளுக்கான இயந்திர மற்றும் பிளாஸ்டிக் பொம்மைகள்"
    },
    category: "General Consumer Goods",
    intendedUse: "Domestic / Household",
    country: "India",
    mfgType: "DOMESTIC_MANUFACTURER",
    standard: "IS 9873 (Part 1):2019"
  },
  {
    label: "Smartphone Fast Charger (Scheme-II CRS / SDoC)",
    labels: {
      en: "Smartphone Fast Charger (Scheme-II CRS / SDoC)",
      hi: "स्मार्टफोन फास्ट चार्जर (योजना-II सीआरएस / एसडीओसी)",
      ta: "ஸ்மார்ட்போன் வேகமான சார்ஜர் (திட்டம்-II சிஆர்எஸ் / எஸ்டிஓசி)"
    },
    name: "Smartphone Fast Power Adapter",
    names: {
      en: "Smartphone Fast Power Adapter",
      hi: "स्मार्टफोन फास्ट पावर एडाप्टर",
      ta: "ஸ்மார்ட்போன் வேகமான பவர் அடாப்டர்"
    },
    category: "Electronics & IT Goods",
    intendedUse: "Commercial / Professional",
    country: "Foreign Country (Import)",
    mfgType: "FOREIGN_MANUFACTURER",
    standard: "IS 13252 (Part 1):2010"
  },
  {
    label: "Imported Ceramic Tiles / Steel (Scheme-I FMCS Foreign Plant)",
    labels: {
      en: "Imported Ceramic Tiles / Steel (Scheme-I FMCS Foreign Plant)",
      hi: "आयातित सिरेमिक टाइलें / स्टील (योजना-I एफएमसीएस विदेशी संयंत्र)",
      ta: "இறக்குமதி செய்யப்பட்ட பீங்கான் ஓடுகள் / எஃகு (திட்டம்-I எஃப்எம்சிஎஸ் வெளிநாட்டு ஆலை)"
    },
    name: "Vitrified Ceramic Tiles & Slabs",
    names: {
      en: "Vitrified Ceramic Tiles & Slabs",
      hi: "विट्रीफाइड सिरेमिक टाइलें और स्लैब",
      ta: "விட்ரிஃபைட் பீங்கான் ஓடுகள் மற்றும் அடுக்குகள்"
    },
    category: "Building Materials & Ceramics",
    intendedUse: "Domestic / Household",
    country: "Germany",
    mfgType: "FOREIGN_MANUFACTURER",
    standard: "IS 15622:2017"
  },
  {
    label: "Biodegradable Detergent (ECO Mark Scheme)",
    labels: {
      en: "Biodegradable Detergent (ECO Mark Scheme)",
      hi: "बायोडिग्रेडेबल डिटर्जेंट (इको मार्क योजना)",
      ta: "மக்கும் சோப்புத்தூள் (ஈகோ மார்க் திட்டம்)"
    },
    name: "Environment-Friendly Laundry Detergent",
    names: {
      en: "Environment-Friendly Laundry Detergent",
      hi: "पर्यावरण-अनुकूल कपड़े धोने का डिटर्जेंट",
      ta: "சுற்றுச்சூழலுக்கு உகந்த சலவை சோப்புத்தூள்"
    },
    category: "Chemicals & Consumer Products",
    intendedUse: "Domestic / Household",
    country: "India",
    mfgType: "DOMESTIC_MANUFACTURER",
    standard: "IS 4955:2020"
  },
  {
    label: "Industrial Machinery (Scheme-X Capital Goods)",
    labels: {
      en: "Industrial Machinery (Scheme-X Capital Goods)",
      hi: "औद्योगिक मशीनरी (योजना-X पूंजीगत सामान)",
      ta: "தொழில்துறை இயந்திரங்கள் (திட்டம்-X மூலதன பொருட்கள்)"
    },
    name: "Industrial Centrifugal Pump & Compressor",
    names: {
      en: "Industrial Centrifugal Pump & Compressor",
      hi: "औद्योगिक सेंट्रीफ्यूगल पंप और कंप्रेसर",
      ta: "தொழில்துறை மையவிலக்கு பம்ப் மற்றும் அமுக்கி"
    },
    category: "Industrial Machinery & Capital Goods",
    intendedUse: "Heavy Industrial",
    country: "India",
    mfgType: "DOMESTIC_MANUFACTURER",
    standard: ""
  },
  {
    label: "Gold Jewellery (Hallmarking with HUID)",
    labels: {
      en: "Gold Jewellery (Hallmarking with HUID)",
      hi: "स्वर्ण आभूषण (एचयूआईडी के साथ हॉलमार्किंग)",
      ta: "தங்க நகைகள் (எச்யுஐடி உடன் ஹால்மார்க்கிங்)"
    },
    name: "22K Gold Jewellery & Ornaments",
    names: {
      en: "22K Gold Jewellery & Ornaments",
      hi: "22K सोने के आभूषण एवं गहने",
      ta: "22K தங்க நகைகள் மற்றும் ஆபரணங்கள்"
    },
    category: "Precious Metals & Jewellery",
    intendedUse: "Domestic / Household",
    country: "India",
    mfgType: "DOMESTIC_MANUFACTURER",
    standard: "IS 1417:2016"
  },
  {
    label: "ISO 9001 Quality Management (Scheme-IV MSCS)",
    labels: {
      en: "ISO 9001 Quality Management (Scheme-IV MSCS)",
      hi: "आईएसओ 9001 गुणवत्ता प्रबंधन (योजना-IV एमएससीएस)",
      ta: "ஐஎஸ்ஓ 9001 தர மேலாண்மை (திட்டம்-IV எம்எஸ்சிஎஸ்)"
    },
    name: "Organizational Quality Management System",
    names: {
      en: "Organizational Quality Management System",
      hi: "संगठनात्मक गुणवत्ता प्रबंधन प्रणाली",
      ta: "நிறுவன தர மேலாண்மை அமைப்பு"
    },
    category: "Management Systems & Auditing",
    intendedUse: "Corporate Enterprise",
    country: "India",
    mfgType: "DOMESTIC_MANUFACTURER",
    standard: "IS/ISO 9001:2015"
  }
];

const OFFICIAL_SOURCES_LOCALIZATION: Record<
  string,
  Record<string, { title: string; desc: string; date?: string }>
> = {
  hi: {
    "Products under Compulsory Certification": {
      title: "अनिवार्य प्रमाणन के अंतर्गत उत्पाद",
      desc: "अनिवार्य गुणवत्ता नियंत्रण आदेशों (QCO) के तहत उत्पादों और भारतीय मानकों की आधिकारिक राजपत्रित सूची।",
      date: "वर्तमान आधिकारिक राजपत्र",
    },
    "Product Certification Process (Scheme-I)": {
      title: "उत्पाद प्रमाणन प्रक्रिया (योजना-I)",
      desc: "योजना-I के तहत मानक संचालन प्रक्रियाएं, कारखाना लेखापरीक्षा मानदंड और नमूना परीक्षण दिशानिर्देश।",
      date: "बीआईएस अनुरूपता विनियम 2018",
    },
    "Product-Specific Guidelines": {
      title: "उत्पाद-विशिष्ट दिशानिर्देश",
      desc: "भारतीय मानकों, निरीक्षण एवं परीक्षण योजना (SIT) और कच्चे माल के मानदंडों के लिए उत्पाद-विशिष्ट दिशानिर्देश।",
      date: "मानक संशोधन के अनुसार अद्यतन",
    },
    "BIS Fee Information & Cost Schedule": {
      title: "बीआईएस शुल्क जानकारी एवं लागत अनुसूची",
      desc: "निर्धारित आवेदन शुल्क, मूल्यांकन शुल्क, प्रयोगशाला परीक्षण दरें और वार्षिक अंकन शुल्क।",
      date: "आधिकारिक बीआईएस शुल्क अनुसूची",
    },
    "ManakOnline Single-Window Portal": {
      title: "मानकऑनलाइन सिंगल-विंडो पोर्टल",
      desc: "बीआईएस योजना-I, सीआरएस और एफएमसीएस आवेदनों के ई-फाइलिंग के लिए भारत सरकार का आधिकारिक पोर्टल।",
      date: "सक्रिय पोर्टल",
    },
  },
  ta: {
    "Products under Compulsory Certification": {
      title: "கட்டாய சான்றிதழின் கீழ் உள்ள பொருட்கள்",
      desc: "கட்டாய தரக் கட்டுப்பாட்டு ஆணைகளின் (QCOs) கீழ் உள்ள பொருட்கள் மற்றும் இந்திய தரநிலைகளின் அதிகாரப்பூர்வ அரசிதழ் பட்டியல்.",
      date: "தற்போதைய அதிகாரப்பூர்வ அரசிதழ்",
    },
    "Product Certification Process (Scheme-I)": {
      title: "தயாரிப்பு சான்றிதழ் செயல்முறை (திட்டம்-I)",
      desc: "திட்டம்-I இன் கீழ் நிலையான செயல்பாட்டு நடைமுறைகள், தொழிற்சாலை தணிக்கை விதிமுறைகள் மற்றும் மாதிரி சோதனை வழிகாட்டுதல்கள்.",
      date: "BIS இணக்க விதிமுறைகள் 2018",
    },
    "Product-Specific Guidelines": {
      title: "தயாரிப்பு சார்ந்த வழிகாட்டுதல்கள்",
      desc: "இந்திய தரநிலைகள், ஆய்வு & சோதனைத் திட்டம் (SIT) மற்றும் மூலப்பொருள் விதிமுறைகளுக்கான தயாரிப்பு சார்ந்த வழிகாட்டுதல்கள்.",
      date: "தரநிலை திருத்தத்தின்படி புதுப்பிக்கப்பட்டது",
    },
    "BIS Fee Information & Cost Schedule": {
      title: "BIS கட்டண தகவல் & செலவு அட்டவணை",
      desc: "விதிக்கப்பட்ட விண்ணப்பக் கட்டணம், மதிப்பீட்டுக் கட்டணங்கள், ஆய்வக சோதனைக் கட்டணங்கள் மற்றும் வருடாந்திர முத்திரைக் கட்டணங்கள்.",
      date: "அதிகாரப்பூர்வ BIS கட்டண அட்டவணை",
    },
    "ManakOnline Single-Window Portal": {
      title: "மானக்ஆன்லைன் ஒற்றைச் சாளர போர்டல்",
      desc: "BIS திட்டம்-I, CRS மற்றும் FMCS விண்ணப்பங்களை மின்-தாக்கல் செய்வதற்கான இந்திய அரசின் அதிகாரப்பூர்வ போர்டல்.",
      date: "செயலில் உள்ள போர்டல்",
    },
  },
};

function CertificationContent() {
  const { t, language } = useLanguage();
  const searchParams = useSearchParams();

  // Form State
  const initialStandard = searchParams.get("standard") || "";
  const [productName, setProductName] = useState(initialStandard ? "" : "Electric Ceiling Fan");
  const [productCategory, setProductCategory] = useState("Electrical Equipment & Appliances");
  const [intendedUse, setIntendedUse] = useState("Domestic / Household");
  const [countryOfManufacture, setCountryOfManufacture] = useState("India");
  const [manufacturerType, setManufacturerType] = useState("DOMESTIC_MANUFACTURER");
  const [standardNumber, setStandardNumber] = useState(initialStandard || "IS 17803:2022");
  const [productDescription, setProductDescription] = useState("");

  // Response & UI state
  const [activeRoadmap, setActiveRoadmap] = useState<CertificationRoadmapResponse | null>(null);
  const [schemes, setSchemes] = useState<CertificationScheme[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"wizard" | "schemes">("wizard");
  const [checklistFilter, setChecklistFilter] = useState<string>("ALL");

  // Schemes Directory Filters
  const [schemeSearch, setSchemeSearch] = useState<string>("");
  const [schemeScope, setSchemeScope] = useState<string>("ALL");
  const [schemeClassification, setSchemeClassification] = useState<string>("ALL");

  const evaluateGuidance = useCallback(
    (customPayload?: Partial<CertificationRoadmapRequest>) => {
      setLoading(true);
      setError(null);

      const payload: CertificationRoadmapRequest = {
        product_name: customPayload?.product_name !== undefined ? customPayload.product_name : productName,
        product_category: customPayload?.product_category !== undefined ? customPayload.product_category : productCategory,
        intended_use: customPayload?.intended_use !== undefined ? customPayload.intended_use : intendedUse,
        country_of_manufacture: customPayload?.country_of_manufacture !== undefined ? customPayload.country_of_manufacture : countryOfManufacture,
        manufacturer_type: customPayload?.manufacturer_type !== undefined ? customPayload.manufacturer_type : manufacturerType,
        product_description: customPayload?.product_description !== undefined ? customPayload.product_description : productDescription,
        standard_number: customPayload?.standard_number !== undefined ? customPayload.standard_number : standardNumber,
        scheme_code: customPayload?.scheme_code,
        language: customPayload?.language || language,
      };

      generateCertificationRoadmap(payload)
        .then((data) => {
          setActiveRoadmap(data);
          setError(null);
        })
        .catch((err) => {
          console.error("Certification guidance evaluation failed:", err);
          setError(err.message || "Unable to evaluate certification guidance. Please check parameters.");
        })
        .finally(() => setLoading(false));
    },
    [
      productName,
      productCategory,
      intendedUse,
      countryOfManufacture,
      manufacturerType,
      productDescription,
      standardNumber,
      language
    ]
  );

  // Load Schemes with dynamic filtering
  useEffect(() => {
    listCertificationSchemes(
      language,
      schemeSearch || undefined,
      schemeScope !== "ALL" ? schemeScope : undefined,
      schemeClassification !== "ALL" ? schemeClassification : undefined
    )
      .then((data) => setSchemes(data))
      .catch((err) => console.error("Failed to load schemes:", err));
  }, [language, schemeSearch, schemeScope, schemeClassification]);

  // Initial evaluation
  useEffect(() => {
    evaluateGuidance();
  }, [language, evaluateGuidance]); // Re-evaluate when language or evaluateGuidance changes


  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    evaluateGuidance();
  };

  const applyPreset = (preset: PresetExample) => {
    const localizedName = preset.names?.[language] || preset.name;
    setProductName(localizedName);
    setProductCategory(preset.category);
    setIntendedUse(preset.intendedUse);
    setCountryOfManufacture(preset.country);
    setManufacturerType(preset.mfgType);
    setStandardNumber(preset.standard);
    setProductDescription("");

    evaluateGuidance({
      product_name: preset.name,
      product_category: preset.category,
      intended_use: preset.intendedUse,
      country_of_manufacture: preset.country,
      manufacturer_type: preset.mfgType,
      standard_number: preset.standard,
      product_description: "",
      language,
    });
  };

  // Filtered document checklist
  const filteredChecklist = useMemo(() => {
    if (!activeRoadmap || !activeRoadmap.document_checklist) return [];
    if (checklistFilter === "ALL") return activeRoadmap.document_checklist;
    return activeRoadmap.document_checklist.filter(
      (item) => item.category === checklistFilter
    );
  }, [activeRoadmap, checklistFilter]);

  return (
    <div className="space-y-8 pb-16">
      {/* GovTech Header Banner */}
      <div className="bg-gradient-to-br from-[#071324] via-[#0d213a] to-[#152E4D] text-white p-6 sm:p-8 rounded-3xl shadow-xl border border-slate-800 relative overflow-hidden">
        {/* Subtle decorative background accent */}
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute right-32 -bottom-20 w-48 h-48 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2.5">
              <div className="bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold text-[11px] px-3 py-1 rounded-full flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                <span>{t("certification.badge", "National Guidance Centre")}</span>
              </div>
              <span className="text-[11px] bg-slate-800/80 text-blue-200 border border-slate-600/60 font-semibold px-2.5 py-0.5 rounded-full">
                BIS Act 2016 Conformity Assessment Framework
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              {t("certification.title", "BIS Product Certification Guidance Centre")}
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              {t(
                "certification.subtitle",
                "Interactive compliance navigator for Indian & Global Manufacturers to determine BIS certification routes, Scheme I, CRS, FMCS, Scheme X, and document checklists."
              )}
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex bg-slate-900/80 p-1.5 rounded-xl border border-slate-700/80 text-xs font-bold shrink-0 shadow-inner">
            <button
              onClick={() => setActiveTab("wizard")}
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                activeTab === "wizard"
                  ? "bg-amber-500 text-slate-950 shadow-md font-extrabold"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{t("certification.wizard_tab", "Product Guidance Navigator")}</span>
            </button>
            <button
              onClick={() => setActiveTab("schemes")}
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                activeTab === "schemes"
                  ? "bg-white text-slate-950 shadow-md font-extrabold"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>{t("certification.schemes_tab", "BIS Schemes Directory")}</span>
            </button>
          </div>
        </div>
      </div>

      {activeTab === "wizard" && (
        <div className="space-y-8">
          {/* Main Product Guidance Input Form */}
          <div className="bg-white p-6 sm:p-7 rounded-2xl border border-slate-200 shadow-sm space-y-5">
            <div className="border-b border-slate-100 pb-3 flex flex-col sm:flex-row justify-between sm:items-center gap-2">
              <div>
                <h2 className="text-base font-extrabold text-slate-900 flex items-center space-x-2">
                  <Factory className="w-4 h-4 text-bis-navy" />
                  <span>{t("certification.generate_title", "Product Certification Guidance Form")}</span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {t(
                    "certification.generate_desc",
                    "Provide your product details, manufacturing location, and applicant context to determine the applicable BIS certification route:"
                  )}
                </p>
              </div>

              <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md self-start sm:self-auto">
                {t("certification.preset_intel_badge", "Deterministic Scheme Intelligence • Source Grounded")}
              </span>
            </div>

            {/* Quick Preset Buttons */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-600">
                {t("certification.quick_examples", "Quick Presets:")}
              </span>
              <div className="flex flex-wrap gap-2">
                {PRESET_EXAMPLES.map((preset) => {
                  const displayLabel = preset.labels?.[language] || preset.label;
                  return (
                    <button
                      key={preset.label}
                      type="button"
                      onClick={() => applyPreset(preset)}
                      className="text-xs bg-slate-50 hover:bg-amber-50 hover:text-amber-900 hover:border-amber-300 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-200 transition-all font-medium flex items-center space-x-1"
                    >
                      <span>{displayLabel}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Interactive Multi-Field Form */}
            <form onSubmit={handleFormSubmit} className="space-y-4 pt-2">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* 1. Product Name */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-800 flex items-center justify-between">
                    <span>{t("certification.product_name_label", "Product Name")} <span className="text-red-500">*</span></span>
                  </label>
                  <input
                    type="text"
                    required
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder={t("certification.input_placeholder", "e.g. Electric Ceiling Fan, Packaged Drinking Water...")}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-navy focus:bg-white transition-all text-slate-900 font-medium"
                  />
                </div>

                {/* 2. Product Category */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-800">
                    {t("certification.product_category_label", "Product Category")}
                  </label>
                  <select
                    value={productCategory}
                    onChange={(e) => setProductCategory(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-navy focus:bg-white transition-all text-slate-900 font-medium"
                  >
                    <option value="Electrical Equipment & Appliances">{t("certification.category_electrical", "Electrical Equipment & Appliances")}</option>
                    <option value="Electronics & IT Goods">{t("certification.category_electronics", "Electronics & IT Goods")}</option>
                    <option value="General Consumer Goods">{t("certification.category_general", "General Consumer Goods")}</option>
                    <option value="Industrial Machinery & Capital Goods">{t("certification.category_machinery", "Industrial Machinery & Capital Goods")}</option>
                    <option value="Precious Metals & Jewellery">{t("certification.category_precious", "Precious Metals & Jewellery")}</option>
                    <option value="Food Products & Packaged Water">{t("certification.category_food", "Food Products & Packaged Water")}</option>
                    <option value="Chemicals & Petrochemicals">{t("certification.category_chemicals", "Chemicals & Petrochemicals")}</option>
                  </select>
                </div>

                {/* 3. Intended Use */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-800">
                    {t("certification.intended_use_label", "Intended Use")}
                  </label>
                  <select
                    value={intendedUse}
                    onChange={(e) => setIntendedUse(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-navy focus:bg-white transition-all text-slate-900 font-medium"
                  >
                    <option value="Domestic / Household">{t("certification.use_household", "Domestic / Household")}</option>
                    <option value="Commercial / Professional">{t("certification.use_commercial", "Commercial / Professional")}</option>
                    <option value="Heavy Industrial">{t("certification.use_industrial", "Heavy Industrial")}</option>
                    <option value="Healthcare / Medical">{t("certification.use_medical", "Healthcare / Medical")}</option>
                  </select>
                </div>

                {/* 4. Country of Manufacture */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <Globe2 className="w-3.5 h-3.5 text-slate-500" />
                    <span>{t("certification.country_label", "Country of Manufacture")}</span>
                  </label>
                  <select
                    value={countryOfManufacture}
                    onChange={(e) => {
                      const val = e.target.value;
                      setCountryOfManufacture(val);
                      if (val !== "India" && manufacturerType === "DOMESTIC_MANUFACTURER") {
                        setManufacturerType("FOREIGN_MANUFACTURER");
                      } else if (val === "India" && manufacturerType === "FOREIGN_MANUFACTURER") {
                        setManufacturerType("DOMESTIC_MANUFACTURER");
                      }
                    }}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-navy focus:bg-white transition-all text-slate-900 font-medium"
                  >
                    <option value="India">{t("certification.domestic_india", "India (Domestic)")}</option>
                    <option value="Foreign Country (Import)">{t("certification.foreign_country", "Foreign Country (Import)")}</option>
                  </select>
                </div>

                {/* 5. Manufacturer / Importer Context */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-800">
                    {t("certification.manufacturer_type_label", "Manufacturer / Importer Context")}
                  </label>
                  <select
                    value={manufacturerType}
                    onChange={(e) => setManufacturerType(e.target.value)}
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-navy focus:bg-white transition-all text-slate-900 font-medium"
                  >
                    <option value="DOMESTIC_MANUFACTURER">{t("certification.type_domestic_oem", "Domestic Manufacturer (OEM)")}</option>
                    <option value="FOREIGN_MANUFACTURER">{t("certification.type_foreign_oem", "Foreign Manufacturer (Overseas Factory)")}</option>
                    <option value="AUTHORIZED_INDIAN_REPRESENTATIVE">{t("certification.type_air", "Authorized Indian Representative (AIR)")}</option>
                    <option value="IMPORTER_TRADER">{t("certification.type_importer", "Importer / Brand Owner / Trader")}</option>
                  </select>
                </div>

                {/* 6. Indian Standard (Optional) */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-800">
                    {t("certification.standard_optional_label", "Applicable Indian Standard (Optional)")}
                  </label>
                  <input
                    type="text"
                    value={standardNumber}
                    onChange={(e) => setStandardNumber(e.target.value)}
                    placeholder="e.g. IS 1293:2019, IS 13252..."
                    className="w-full px-3.5 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-navy focus:bg-white transition-all text-slate-900 font-mono"
                  />
                </div>
              </div>

              {/* 7. Product Description (Optional) */}
              <div className="space-y-1.5 pt-1">
                <label className="text-xs font-bold text-slate-800">
                  {t("certification.product_desc_optional_label", "Technical Specifications / Key Ratings (Optional)")}
                </label>
                <input
                  type="text"
                  value={productDescription}
                  onChange={(e) => setProductDescription(e.target.value)}
                  placeholder="e.g. 240V AC 50Hz, BLDC Motor, 1200mm sweep, Class I insulation..."
                  className="w-full px-3.5 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-navy focus:bg-white transition-all text-slate-900"
                />
              </div>

              {/* Submit Button */}
              <div className="pt-2 flex justify-end">
                <button
                  type="submit"
                  disabled={loading || !productName.trim()}
                  className="w-full sm:w-auto bg-[#0f294a] hover:bg-[#1a3a5f] text-white font-extrabold px-8 py-3 rounded-xl text-xs sm:text-sm transition-all shadow-md flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>
                    {loading
                      ? t("certification.generating_btn", "Evaluating...")
                      : t("certification.generate_btn", "Evaluate Certification Pathway")}
                  </span>
                </button>
              </div>
            </form>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-xs text-red-900 flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-bold">Error Generating Guidance</p>
                <p>{error}</p>
              </div>
            </div>
          )}

          {/* Guidance Evaluation Results Display */}
          {activeRoadmap && (
            <div className="space-y-8">
              {/* Route Pathway Summary Card */}
              <div className="bg-gradient-to-br from-[#0a2540] via-[#0f294a] to-[#143257] text-white p-6 sm:p-8 rounded-2xl border border-slate-700/80 shadow-md space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-black uppercase tracking-wider text-amber-300 bg-amber-500/20 border border-amber-500/40 px-3 py-1 rounded-full">
                      {activeRoadmap.applicable_scheme || "SCHEME_I_ISI"}
                    </span>

                    {activeRoadmap.evidence_level === "VERIFIED_STANDARD_MATCH" ? (
                      <span className="text-xs font-bold text-emerald-300 bg-emerald-950/60 border border-emerald-500/40 px-3 py-1 rounded-full flex items-center space-x-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        <span>{t("certification.guidance_status_verified", "Verified Standard Match")}</span>
                      </span>
                    ) : (
                      <span className="text-xs font-bold text-blue-300 bg-blue-950/60 border border-blue-500/40 px-3 py-1 rounded-full flex items-center space-x-1">
                        <Info className="w-3.5 h-3.5 text-blue-400" />
                        <span>{t("certification.guidance_status_preliminary", "Preliminary Technical Guidance")}</span>
                      </span>
                    )}

                    {activeRoadmap.is_mandatory_qco && (
                      <span className="text-xs font-bold text-red-300 bg-red-950/60 border border-red-500/50 px-3 py-1 rounded-full flex items-center space-x-1">
                        <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
                        <span>{t("certification.qco_enforced", "Mandatory QCO Enforced")}</span>
                      </span>
                    )}

                    {activeRoadmap.requires_air && (
                      <span className="text-xs font-bold text-purple-200 bg-purple-950/60 border border-purple-500/40 px-3 py-1 rounded-full">
                        {t("certification.air_required_badge", "Authorized Indian Representative (AIR) Required")}
                      </span>
                    )}
                  </div>

                  {activeRoadmap.standard_number && (
                    <Link
                      href={`/standards/${encodeURIComponent(activeRoadmap.standard_number)}`}
                      className="text-xs font-mono font-bold text-amber-300 hover:text-amber-200 bg-slate-800/80 hover:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-600 transition-all flex items-center space-x-1.5"
                    >
                      <span>{t("certification.standard_link", "Standard:")} {activeRoadmap.standard_number}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  )}
                </div>

                <div className="space-y-1 pt-1">
                  <h2 className="text-xl sm:text-2xl font-extrabold leading-tight text-white">
                    {t("certification.pathway_title", "Recommended Certification Pathway:")} {activeRoadmap.product}
                  </h2>
                  <p className="text-xs sm:text-sm text-slate-300 font-medium">
                    {t("certification.applicable_process", "Applicable Route:")}{" "}
                    <strong className="text-amber-300">{activeRoadmap.scheme_name}</strong>
                  </p>
                </div>

                {/* Route Rationale Box */}
                <div className="bg-slate-900/70 p-4 sm:p-5 rounded-xl border border-slate-700/80 space-y-2 mt-2">
                  <h3 className="text-xs font-extrabold uppercase tracking-wider text-amber-400 flex items-center space-x-1.5">
                    <Scale className="w-4 h-4" />
                    <span>{t("certification.route_rationale_title", "Certification Route Rationale & Analysis")}</span>
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                    {activeRoadmap.route_rationale}
                  </p>
                </div>
              </div>

              {/* Clarifying Questions Card (if any) */}
              {activeRoadmap.clarifying_questions && activeRoadmap.clarifying_questions.length > 0 && (
                <div className="bg-amber-50/80 border border-amber-200/90 rounded-2xl p-5 sm:p-6 space-y-3">
                  <div className="flex items-center space-x-2">
                    <HelpCircle className="w-5 h-5 text-amber-700 shrink-0" />
                    <h3 className="text-sm font-bold text-amber-950">
                      {t("certification.clarifying_questions_title", "Clarifying Compliance Questions")}
                    </h3>
                  </div>
                  <p className="text-xs text-amber-900 leading-relaxed">
                    {t(
                      "certification.clarifying_questions_desc",
                      "Information required to confirm exact scope and standard applicability:"
                    )}
                  </p>
                  <ul className="space-y-2 pt-1">
                    {activeRoadmap.clarifying_questions.map((q, idx) => (
                      <li
                        key={idx}
                        className="flex items-start space-x-2.5 text-xs text-amber-950 bg-white/90 p-3 rounded-xl border border-amber-200 shadow-sm"
                      >
                        <span className="w-5 h-5 rounded-full bg-amber-200 text-amber-900 font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span className="leading-relaxed font-medium">{q}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 6-Stage Compliance Guide */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-extrabold text-slate-900 flex items-center space-x-2">
                    <Layers className="w-5 h-5 text-bis-navy" />
                    <span>{t("certification.roadmap_title", "6-Stage Step-by-Step Compliance Guide")}</span>
                  </h3>
                  <span className="text-xs font-semibold text-slate-500">
                    Stage 1 through 6
                  </span>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {activeRoadmap.steps.map((step) => (
                    <div
                      key={step.step_number}
                      className="bg-white p-5 sm:p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-bis-navy/50 transition-all space-y-3 relative overflow-hidden"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-[#0f294a] text-white text-xs font-black flex items-center justify-center shrink-0 shadow-sm">
                            {step.step_number}
                          </div>
                          <h4 className="font-extrabold text-slate-900 text-sm sm:text-base">
                            {step.title}
                          </h4>
                        </div>

                        {step.status_badge && (
                          <span className="text-[11px] font-bold text-[#0f294a] bg-blue-50 border border-blue-200 px-3 py-1 rounded-full self-start sm:self-auto">
                            {step.status_badge}
                          </span>
                        )}
                      </div>

                      <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-0 sm:pl-11">
                        {step.description}
                      </p>

                      {step.checklist && step.checklist.length > 0 && (
                        <div className="pl-0 sm:pl-11 pt-2 space-y-2">
                          <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                            {t("certification.action_items", "Action Items & Required Verifications:")}
                          </p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {step.checklist.map((item, idx) => (
                              <div
                                key={idx}
                                className="flex items-start space-x-2 text-xs text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-100"
                              >
                                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                                <span className="leading-snug">{item}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Dynamic Categorized Document Checklist */}
              {activeRoadmap.document_checklist && activeRoadmap.document_checklist.length > 0 && (
                <div className="bg-white p-6 sm:p-7 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div>
                      <h3 className="text-base font-extrabold text-slate-900 flex items-center space-x-2">
                        <FileCheck className="w-5 h-5 text-emerald-600" />
                        <span>{t("certification.checklist_title", "Dynamic Document Checklist")}</span>
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {t(
                          "certification.checklist_desc",
                          "Categorized requirements distinguishing verified official statutory mandates from general preparation guidance."
                        )}
                      </p>
                    </div>

                    {/* Category Filter Pills */}
                    <div className="flex flex-wrap gap-1.5 bg-slate-100 p-1 rounded-xl text-xs font-bold">
                      {[
                        { id: "ALL", label: t("certification.cat_all", "All Documents") },
                        { id: "LEGAL_INCORPORATION", label: t("certification.cat_legal", "Legal & Incorporation") },
                        { id: "TECHNICAL_FACILITY", label: t("certification.cat_technical", "Plant & Machinery") },
                        { id: "TESTING_CALIBRATION", label: t("certification.cat_testing", "Testing & Calibration") },
                        ...(activeRoadmap.requires_air
                          ? [{ id: "AIR_FOREIGN", label: t("certification.cat_air", "AIR & Foreign OEM") }]
                          : []),
                      ].map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setChecklistFilter(tab.id)}
                          className={`px-3 py-1 rounded-lg transition-all text-[11px] ${
                            checklistFilter === tab.id
                              ? "bg-white text-slate-900 shadow-sm font-extrabold"
                              : "text-slate-600 hover:text-slate-900"
                          }`}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                    {filteredChecklist.map((doc, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-50 p-4 rounded-xl border border-slate-200 hover:border-slate-300 transition-all space-y-2 flex flex-col justify-between"
                      >
                        <div className="space-y-1.5">
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex items-start space-x-2">
                              <CheckSquare className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                              <span className="text-xs font-bold text-slate-900 leading-snug">
                                {doc.item}
                              </span>
                            </div>
                          </div>

                          {doc.note && (
                            <p className="text-[11px] text-slate-500 leading-relaxed pl-6">
                              {doc.note}
                            </p>
                          )}
                        </div>

                        <div className="pt-2 pl-6 flex items-center justify-between border-t border-slate-200/60">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                              doc.is_verified_official
                                ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                                : "bg-amber-100 text-amber-800 border border-amber-300"
                            }`}
                          >
                            {doc.is_verified_official
                              ? t("certification.tag_official", "Official Verified Requirement")
                              : t("certification.tag_general", "General Preparation Guidance")}
                          </span>

                          <span className="text-[10px] font-mono text-slate-400 uppercase">
                            {doc.category}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Official BIS Source Cards */}
              {activeRoadmap.official_sources && activeRoadmap.official_sources.length > 0 && (
                <div className="bg-slate-900 text-white p-6 sm:p-7 rounded-2xl border border-slate-800 shadow-md space-y-4">
                  <div>
                    <h3 className="text-base font-extrabold flex items-center space-x-2 text-white">
                      <Globe2 className="w-5 h-5 text-amber-400" />
                      <span>{t("certification.official_sources_title", "Official BIS Portals & Gazetted References")}</span>
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {t(
                        "certification.official_sources_desc",
                        "Direct verifiable links to official Government of India portals, gazette notifications, and fee schedules:"
                      )}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pt-1">
                    {activeRoadmap.official_sources.map((src, idx) => {
                      const locSource = OFFICIAL_SOURCES_LOCALIZATION[language]?.[src.title];
                      const displayTitle = locSource?.title || src.title;
                      const displayDesc = locSource?.desc || src.description;
                      const displayDate = locSource?.date || src.verification_date;

                      return (
                        <a
                          key={idx}
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="bg-slate-800/90 hover:bg-slate-800 p-4 rounded-xl border border-slate-700 hover:border-amber-400/60 transition-all flex flex-col justify-between space-y-3 group"
                        >
                          <div className="space-y-1.5">
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="text-xs font-bold text-white group-hover:text-amber-300 transition-colors flex items-center space-x-1">
                                <span>{displayTitle}</span>
                                <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-amber-400 shrink-0" />
                              </h4>
                            </div>
                            <p className="text-[11px] text-slate-300 leading-relaxed">
                              {displayDesc}
                            </p>
                          </div>

                          <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-[10px] text-slate-400">
                            <span className="font-mono truncate max-w-[160px] text-blue-300">
                              {src.url.replace("https://", "").replace("www.", "")}
                            </span>
                            {displayDate && (
                              <span className="bg-slate-700 text-slate-300 px-2 py-0.5 rounded font-medium">
                                {displayDate}
                              </span>
                            )}
                          </div>
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Disclaimer Notice Banner */}
              <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 text-xs text-amber-900 flex items-start space-x-3 shadow-sm">
                <Info className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="font-extrabold text-amber-950">
                    {t("certification.disclaimer_title", "Official Disclaimer & Guidance Notice")}
                  </p>
                  <p className="leading-relaxed text-amber-900">
                    {activeRoadmap.disclaimer}
                  </p>
                </div>
              </div>

              {/* Quick Actions & Follow-up Assistant */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="space-y-0.5 text-center sm:text-left">
                  <p className="text-xs font-bold text-slate-900">
                    {t("certification.ready_to_proceed", "Ready to proceed with testing or interactive query?")}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {t(
                      "certification.find_labs_or_ask",
                      "Find accredited laboratories or ask specific questions directly to the Sahayak AI."
                    )}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <Link
                    href={`/laboratories?standard=${encodeURIComponent(activeRoadmap.standard_number || "")}`}
                    className="bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 font-bold px-4 py-2.5 rounded-xl text-xs flex items-center space-x-2 transition-all shadow-sm"
                  >
                    <FlaskConical className="w-4 h-4 text-purple-700" />
                    <span>{t("certification.find_labs_btn", "Find Recognized Labs for this Standard")}</span>
                  </Link>

                  <Link
                    href={`/assistant?prompt=${encodeURIComponent(
                      `I am manufacturing ${activeRoadmap.product} (${activeRoadmap.standard_number || "standard pending"}). The recommended BIS route is ${activeRoadmap.applicable_scheme}. Can you explain the detailed factory audit, testing parameters, and documentation checklist for this specific route?`
                    )}`}
                    className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold px-5 py-2.5 rounded-xl text-xs flex items-center space-x-2 transition-all shadow-md"
                  >
                    <BotMessageSquare className="w-4 h-4 text-slate-950" />
                    <span>{t("certification.ask_workflow_btn", "Ask Sahayak about this Guidance")}</span>
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Schemes Explorer Tab */}
      {activeTab === "schemes" && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="space-y-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="text-base font-extrabold text-slate-900 flex items-center space-x-2">
                  <BookOpen className="w-5 h-5 text-[#0f294a]" />
                  <span>{t("certification.schemes_tab", "BIS Statutory Conformity Assessment Schemes Directory")}</span>
                </h2>
                <span className="bg-blue-50 text-[#0f294a] text-xs font-bold px-3 py-1 rounded-full border border-blue-200">
                  {schemes.length} {t("certification.schemes_verified", "Verified Routes Available")}
                </span>
              </div>
              <p className="text-xs text-slate-500">
                {t(
                  "certification.schemes_directory_subtitle",
                  "Official directory of statutory product certification, self-declaration registration, and conformity assessment routes under the Bureau of Indian Standards Act, 2016 and BIS Conformity Assessment Regulations, 2018."
                )}
              </p>
            </div>

            {/* Search & Scope Filters */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3 pt-2 border-t border-slate-100">
              <div className="md:col-span-7 relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={schemeSearch}
                  onChange={(e) => setSchemeSearch(e.target.value)}
                  placeholder={t("certification.search_schemes_placeholder", "Search schemes by name, keyword, standard, or sector...")}
                  className="w-full bg-slate-50 border border-slate-200 focus:border-[#0f294a] focus:bg-white rounded-xl pl-9 pr-8 py-2.5 text-xs text-slate-900 transition-all outline-none"
                />
                {schemeSearch && (
                  <button
                    onClick={() => setSchemeSearch("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs font-bold"
                  >
                    ×
                  </button>
                )}
              </div>

              <div className="md:col-span-5 flex items-center gap-1.5 overflow-x-auto">
                {[
                  { id: "ALL", label: t("certification.scope_all", "All Scopes") },
                  { id: "DOMESTIC", label: t("certification.scope_domestic", "Domestic") },
                  { id: "FOREIGN", label: t("certification.scope_foreign", "Foreign / FMCS") },
                  { id: "ORGANIZATIONS_AND_LABS", label: t("certification.scope_labs", "Labs & MSCS") }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setSchemeScope(tab.id)}
                    className={`px-3 py-2 rounded-xl text-xs font-bold transition-all shrink-0 ${
                      schemeScope === tab.id
                        ? "bg-[#0f294a] text-white shadow-sm"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Schemes Grid */}
          {schemes.length === 0 ? (
            <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
              <Info className="w-8 h-8 text-slate-400 mx-auto" />
              <p className="text-sm font-bold text-slate-700">{t("certification.no_schemes_found", "No matching BIS schemes found")}</p>
              <p className="text-xs text-slate-500">{t("certification.try_adjusting_filters", "Try adjusting your search keywords or resetting the manufacturer scope filter.")}</p>
              <button
                onClick={() => {
                  setSchemeSearch("");
                  setSchemeScope("ALL");
                }}
                className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold px-4 py-2 rounded-xl text-xs transition-all"
              >
                {t("certification.reset_filters", "Reset Filters")}
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {schemes.map((scheme) => (
                <div
                  key={scheme.scheme_code}
                  className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-[#0f294a] transition-all flex flex-col justify-between space-y-5 group"
                >
                  <div className="space-y-4">
                    {/* Header Badges */}
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-black text-[#0f294a] bg-blue-50 px-2.5 py-1 rounded-md border border-blue-200 inline-block">
                          {scheme.scheme_code}
                        </span>
                        {scheme.manufacturer_scope && (
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                            scheme.manufacturer_scope === "FOREIGN"
                              ? "bg-purple-50 text-purple-800 border-purple-200"
                              : scheme.manufacturer_scope === "DOMESTIC"
                              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                              : "bg-amber-50 text-amber-800 border-amber-200"
                          }`}>
                            {scheme.manufacturer_scope.replace("_", " ")}
                          </span>
                        )}
                      </div>

                      {scheme.data_confidence && (
                        <span className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full font-bold flex items-center space-x-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>{t("certification.statutory_verified", "Statutory Verified")}</span>
                        </span>
                      )}
                    </div>

                    {/* Title & Classification */}
                    <div className="space-y-1">
                      <h3 className="font-black text-slate-900 text-base group-hover:text-[#0f294a] transition-colors leading-snug">
                        {scheme.name}
                      </h3>
                      {scheme.classification && (
                        <p className="text-[11px] font-bold text-blue-700">
                          {scheme.classification}
                        </p>
                      )}
                    </div>

                    {/* Description */}
                    <p className="text-xs text-slate-600 leading-relaxed">
                      {scheme.description}
                    </p>

                    {/* Legal Act & Official Citation */}
                    {scheme.legal_act_and_regulation && (
                      <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1 text-[11px]">
                        <p className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                          <Scale className="w-3 h-3 text-slate-600" />
                          <span>{t("certification.statutory_authority", "Statutory Authority & Regulations")}</span>
                        </p>
                        <p className="text-slate-700 font-medium leading-relaxed">
                          {scheme.legal_act_and_regulation}
                        </p>
                      </div>
                    )}

                    {/* Covered Sectors */}
                    {scheme.applicable_sectors && scheme.applicable_sectors.length > 0 && (
                      <div className="space-y-1.5">
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                          {t("certification.covered_sectors", "Covered Sectors & Product Scopes")}
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {scheme.applicable_sectors.map((sec) => (
                            <span
                              key={sec}
                              className="text-[10px] bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md font-medium"
                            >
                              {sec}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Fee Structure Summary */}
                    {scheme.fee_structure_summary && (
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                          {t("certification.fee_structure", "Fee Structure & Testing Charges")}
                        </p>
                        <p className="text-[11px] text-slate-600 bg-amber-50/60 p-2.5 rounded-xl border border-amber-100/80 leading-relaxed font-medium">
                          {scheme.fee_structure_summary}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Actions & Official Reference */}
                  <div className="pt-4 border-t border-slate-100 space-y-3">
                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      {scheme.official_reference_url && (
                        <a
                          href={scheme.official_reference_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-700 hover:text-blue-900 font-bold flex items-center space-x-1 underline decoration-blue-300"
                        >
                          <span>{t("certification.official_bis_portal", "Official BIS Portal / Guidelines")}</span>
                          <ExternalLink className="w-3 h-3 shrink-0" />
                        </a>
                      )}
                      {scheme.source_verification_date && (
                        <span className="text-[10px] text-slate-400 font-mono">
                          {t("certification.verified", "Verified")}: {scheme.source_verification_date}
                        </span>
                      )}
                    </div>

                    <button
                      onClick={() => {
                        setActiveTab("wizard");
                        setProductName(scheme.name);
                        evaluateGuidance({
                          product_name: scheme.name,
                          scheme_code: scheme.scheme_code,
                          language,
                        });
                      }}
                      className="w-full bg-[#0f294a] hover:bg-[#1a4478] text-white font-bold py-2.5 rounded-xl text-xs transition-all shadow-sm flex items-center justify-center space-x-1.5"
                    >
                      <span>{t("certification.generate_for_scheme", "Generate Step-by-Step Roadmap for this Scheme")}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

    </div>
  );
}

export default function CertificationPage() {
  const { t } = useLanguage();
  return (
    <Suspense
      fallback={
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center text-slate-500 text-sm font-medium">
          {t("certification.loading_roadmap", "Loading Certification Guidance Centre...")}
        </div>
      }
    >
      <CertificationContent />
    </Suspense>
  );
}
