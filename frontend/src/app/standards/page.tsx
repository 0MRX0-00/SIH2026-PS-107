"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  FileSearch,
  Filter,
  Search,
  CheckCircle,
  AlertTriangle,
  Building2,
  ArrowRight,
  BotMessageSquare,
  Award,
  FlaskConical,
  ExternalLink,
  ShieldCheck,
  Tag,
  BookOpen,
  Calendar,
  Layers,
} from "lucide-react";
import { listStandards, StandardListItem } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import { localizeStandard } from "@/lib/localizeStandards";

const TECHNICAL_DIVISIONS = [
  "All Technical Divisions",
  "Electrotechnical",
  "Electronics & Information Technology",
  "Civil Engineering",
  "Food and Agriculture",
  "Mechanical Engineering & Consumer Products",
  "Metallurgical Engineering",
  "Chemical",
  "Medical Equipment & Healthcare",
];

const DIVISION_TRANSLATIONS: Record<string, Record<string, string>> = {
  hi: {
    "Electrotechnical": "इलेक्ट्रो-तकनीकी (ETD)",
    "Electronics & Information Technology": "इलेक्ट्रॉनिक्स और सूचना प्रौद्योगिकी (LITD)",
    "Civil Engineering": "सिविल इंजीनियरिंग (CED)",
    "Food and Agriculture": "खाद्य और कृषि (FAD)",
    "Mechanical Engineering & Consumer Products": "मैकेनिकल और उपभोक्ता उत्पाद (MED/PCD)",
    "Metallurgical Engineering": "धातुकर्म इंजीनियरिंग (MTD)",
    "Chemical": "केमिकल (रसायन) (CHD/PCD)",
    "Medical Equipment & Healthcare": "चिकित्सा उपकरण और स्वास्थ्य सेवा (MHD)",
  },
  ta: {
    "Electrotechnical": "மின் தொழில்நுட்பம் (ETD)",
    "Electronics & Information Technology": "மின்னணுவியல் & தகவல் தொழில்நுட்பம் (LITD)",
    "Civil Engineering": "கட்டுமானப் பொறியியல் (CED)",
    "Food and Agriculture": "உணவு மற்றும் விவசாயம் (FAD)",
    "Mechanical Engineering & Consumer Products": "இயந்திர மற்றும் நுகர்வோர் பொருட்கள் (MED/PCD)",
    "Metallurgical Engineering": "உலோகவியல் பொறியியல் (MTD)",
    "Chemical": "வேதியியல் (CHD/PCD)",
    "Medical Equipment & Healthcare": "மருத்துவ உபகரணங்கள் & சுகாதாரம் (MHD)",
  },
};

const CATEGORY_TRANSLATIONS: Record<string, Record<string, string>> = {
  hi: {
    "All Categories": "सभी श्रेणियां",
    "Electrical Wiring Accessories": "विद्युत वायरिंग सहायक उपकरण",
    "Electrical Cables & Wires": "विद्युत केबल एवं तार",
    "IT Equipment & Power Supplies": "आईटी उपकरण एवं बिजली आपूर्ति",
    "Cement & Building Materials": "सीमेंट एवं निर्माण सामग्री",
    "Structural Steel & TMT Rebars": "संरचनात्मक इस्पात एवं टीएमटी",
    "Packaged Water & Beverages": "पैकेज्ड पेयजल एवं पेय पदार्थ",
    "Automotive Batteries & Energy Storage": "ऑटोमोटिव बैटरियां एवं ऊर्जा भंडारण",
    "Protective Safety Equipment": "सुरक्षा उपकरण एवं हेलमेट",
    "Toys & Child Care Products": "खिलौने एवं शिशु देखभाल उत्पाद",
    "Pressure Vessels & Gas Cylinders": "गैस सिलेंडर एवं दबाव वाहिकाएं",
    "Medical Disposables & Devices": "चिकित्सा उपकरण एवं सिरिंज",
  },
  ta: {
    "All Categories": "அனைத்து பிரிவுகள்",
    "Electrical Wiring Accessories": "மின் வயரிங் பாகங்கள்",
    "Electrical Cables & Wires": "மின் கேபிள்கள் மற்றும் கம்பிகள்",
    "IT Equipment & Power Supplies": "தகவல் தொழில்நுட்ப சாதனங்கள்",
    "Cement & Building Materials": "சிமெண்ட் & கட்டுமான பொருட்கள்",
    "Structural Steel & TMT Rebars": "கட்டமைப்பு எஃகு & டிஎம்டி கம்பிகள்",
    "Packaged Water & Beverages": "பாட்டில் குடிநீர் & பானங்கள்",
    "Automotive Batteries & Energy Storage": "வாகன பேட்டரிகள் & ஆற்றல் சேமிப்பு",
    "Protective Safety Equipment": "பாதுகாப்பு உபகரணங்கள்",
    "Toys & Child Care Products": "பொம்மைகள் & குழந்தைகள் பொருட்கள்",
    "Pressure Vessels & Gas Cylinders": "எரிவாயு சிலிண்டர்கள்",
    "Medical Disposables & Devices": "மருத்துவ உபகரணங்கள்",
  },
};

const POPULAR_CATEGORIES = [
  "All Categories",
  "Electrical Wiring Accessories",
  "Electrical Cables & Wires",
  "IT Equipment & Power Supplies",
  "Cement & Building Materials",
  "Structural Steel & TMT Rebars",
  "Packaged Water & Beverages",
  "Automotive Batteries & Energy Storage",
  "Protective Safety Equipment",
  "Toys & Child Care Products",
  "Pressure Vessels & Gas Cylinders",
  "Medical Disposables & Devices",
];

export default function StandardsExplorerPage() {
  const { t, language } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDivision, setSelectedDivision] = useState("All Technical Divisions");
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [qcoOnly, setQcoOnly] = useState(false);
  const [standards, setStandards] = useState<StandardListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const divFilter =
      selectedDivision === "All Technical Divisions" ? undefined : selectedDivision;
    const catFilter =
      selectedCategory === "All Categories" ? undefined : selectedCategory;
    listStandards({
      q: searchQuery || undefined,
      division: divFilter,
      product_category: catFilter,
      qco_only: qcoOnly ? true : undefined,
      limit: 100,
      language,
    })
      .then((data) => setStandards(data))
      .catch((err) => {
        console.error("Failed to load standards:", err);
        setStandards([]);
      })
      .finally(() => setIsLoading(false));
  }, [searchQuery, selectedDivision, selectedCategory, qcoOnly, language]);

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="w-10 h-10 rounded-2xl bg-[#071324] text-amber-400 flex items-center justify-center">
              <FileSearch className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
                  {t("standards.title", "Indian Standards Explorer")}
                </h1>
                <span className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  {t("standards.official_catalogue", "Official BIS Catalogue")}
                </span>
              </div>
              <p className="text-xs text-[#64748B] mt-0.5">
                {t(
                  "standards.subtitle",
                  "Authentic Indian Standards (IS), mandatory Quality Control Orders (QCOs), and technical clauses"
                )}
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="text-xs text-slate-700 bg-slate-50 px-4 py-2 rounded-2xl border border-slate-200 font-bold shadow-xs">
            <span className="text-blue-900 font-extrabold text-sm">
              {standards.length}
            </span>{" "}
            {t("standards.showing_count", "Verified Standards Loaded")}
          </div>
        </div>
      </div>

      {/* Search & Filter Controls */}
      <div className="bg-white p-5 sm:p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t(
                "standards.search_placeholder",
                "Search by standard (e.g. IS 1293), product (cables, cement), or QCO order..."
              )}
              className="w-full pl-10 pr-4 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 focus:bg-white transition-all text-slate-900 placeholder:text-slate-400 shadow-xs"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400 shrink-0" />
            <select
              value={selectedDivision}
              onChange={(e) => setSelectedDivision(e.target.value)}
              className="w-full py-2.5 px-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 text-slate-900 font-medium"
            >
              {TECHNICAL_DIVISIONS.map((div) => {
                const label =
                  div === "All Technical Divisions"
                    ? t("common.all_divisions", "All Technical Divisions")
                    : DIVISION_TRANSLATIONS[language]?.[div] || div;
                return (
                  <option key={div} value={div}>
                    {label}
                  </option>
                );
              })}
            </select>
          </div>
        </div>

        {/* Quick Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <span className="text-[11px] font-bold text-slate-400 shrink-0 flex items-center mr-1">
            <Tag className="w-3 h-3 mr-1" /> {t("standards.category_label", "Category:")}
          </span>
          {POPULAR_CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`shrink-0 px-3 py-1 rounded-lg text-[11px] font-bold transition-all ${
                selectedCategory === cat
                  ? "bg-[#071324] text-amber-400 shadow-xs"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {CATEGORY_TRANSLATIONS[language]?.[cat] || cat}
            </button>
          ))}
        </div>

        {/* Mandatory QCO Checkbox Filter */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 text-xs">
          <label className="flex items-center space-x-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={qcoOnly}
              onChange={(e) => setQcoOnly(e.target.checked)}
              className="rounded text-amber-600 focus:ring-amber-500 w-4 h-4"
            />
            <span className="font-bold text-slate-800 flex items-center">
              <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600" />
              {t(
                "standards.qco_filter",
                "Mandatory Quality Control Orders (QCO) Only"
              )}
            </span>
          </label>

          {(searchQuery ||
            selectedDivision !== "All Technical Divisions" ||
            selectedCategory !== "All Categories" ||
            qcoOnly) && (
            <button
              onClick={() => {
                setSearchQuery("");
                setSelectedDivision("All Technical Divisions");
                setSelectedCategory("All Categories");
                setQcoOnly(false);
              }}
              className="text-xs font-semibold text-rose-600 hover:text-rose-800 transition-colors"
            >
              {t("standards.clear_filters", "Clear Filters")}
            </button>
          )}
        </div>
      </div>

      {/* Results Section */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-500 bg-white rounded-3xl border border-slate-200">
          <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm font-semibold">Loading verified Indian Standards...</p>
        </div>
      ) : standards.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 space-y-3">
          <FileSearch className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="font-bold text-slate-800 text-base">
            No Indian Standards Found
          </h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            No standards matched your query. Try searching by number (e.g. &apos;IS 1293&apos;) or clearing filters.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {standards.map((std) => {
            const loc = localizeStandard(
              std.standard_number,
              std.title,
              std.scope_summary,
              std.division,
              language
            );

            return (
              <div
                key={std.standard_number}
                className="bg-white border border-slate-200 hover:border-amber-500/50 rounded-2xl p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between group"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-black text-sm text-[#071324] bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200 tracking-tight font-mono">
                      {loc.number || std.standard_number}
                    </span>
                    {std.is_qco_mandatory ? (
                      <span className="text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 px-2 py-0.5 rounded-full flex items-center space-x-1 shrink-0">
                        <AlertTriangle className="w-2.5 h-2.5" />
                        <span>{t("standards.qco_mandatory", "QCO Mandatory")}</span>
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full shrink-0">
                        {t("standards.voluntary", "Voluntary")}
                      </span>
                    )}
                  </div>

                  <div>
                    <h3 className="font-bold text-sm text-[#0F172A] group-hover:text-blue-900 transition-colors line-clamp-2">
                      {loc.title}
                    </h3>
                    {loc.scope && (
                      <p className="text-xs text-[#64748B] mt-1.5 line-clamp-3 leading-relaxed">
                        {loc.scope}
                      </p>
                    )}
                  </div>

                  <div className="pt-2 border-t border-slate-100 space-y-1 text-[11px] text-slate-500">
                    <div className="flex items-center justify-between">
                      <span>{t("standards.division_label", "Division:")}</span>
                      <span className="font-semibold text-slate-700 truncate max-w-[180px]">
                        {loc.division}
                      </span>
                    </div>
                    {std.year && (
                      <div className="flex items-center justify-between">
                        <span>{t("standards.edition_year_label", "Edition / Year:")}</span>
                        <span className="font-semibold text-slate-700">{std.year}</span>
                      </div>
                    )}
                    {std.qco_order_number && (
                      <div className="flex items-center justify-between text-amber-800">
                        <span>{t("standards.qco_order_label", "QCO Order:")}</span>
                        <span className="font-mono font-bold truncate max-w-[180px]">
                          {std.qco_order_number}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <Link
                    href={`/standards/${encodeURIComponent(std.standard_number)}`}
                    className="flex-1 text-center bg-[#071324] hover:bg-[#152E4D] text-white text-xs font-semibold py-2 px-3 rounded-xl transition-colors shadow-xs"
                  >
                    {t("standards.view_clauses_btn", "View Clauses & Details")}
                  </Link>

                  <Link
                    href={`/assistant?prompt=${encodeURIComponent(
                      `What are the requirements and clauses in ${std.standard_number}?`
                    )}`}
                    title="Ask Sahayak AI about this standard"
                    className="p-2 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 rounded-xl transition-colors"
                  >
                    <BotMessageSquare className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
