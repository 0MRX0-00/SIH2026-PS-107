"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  FlaskConical,
  MapPin,
  Search,
  Phone,
  Mail,
  Building,
  CheckCircle2,
  Filter,
  Layers,
  BotMessageSquare,
  ShieldCheck,
  AlertCircle,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Clock,
  Sparkles,
  Calendar,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Tag
} from "lucide-react";
import {
  searchLaboratories,
  fetchLaboratoryStats,
  LaboratoryItem,
  LaboratorySearchResponse,
  LaboratoryStats
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import {
  localizeLabName,
  localizeCity,
  localizeState,
  localizeTestingScope,
  localizeRecognitionBadge
} from "@/lib/localizeLab";

const STATE_TRANSLATIONS: Record<string, Record<string, string>> = {
  hi: {
    "Delhi": "दिल्ली",
    "Maharashtra": "महाराष्ट्र",
    "Tamil Nadu": "तमिलनाडु",
    "Uttar Pradesh": "उत्तर प्रदेश",
    "West Bengal": "पश्चिम बंगाल",
    "Karnataka": "कर्नाटक",
    "Gujarat": "गुजरात",
    "Rajasthan": "राजस्थान",
    "Punjab": "पंजाब",
    "Haryana": "हरियाणा",
    "Kerala": "केरल",
    "Madhya Pradesh": "मध्य प्रदेश",
    "Telangana": "तेलंगाना",
    "Andhra Pradesh": "आंध्र प्रदेश",
    "Odisha": "ओडिशा",
    "Bihar": "बिहार",
    "Assam": "असम",
    "Chhattisgarh": "छत्तीसगढ़",
    "Jharkhand": "झारखंड",
    "Uttarakhand": "उत्तराखंड",
    "Himachal Pradesh": "हिमाचल प्रदेश",
    "Jammu & Kashmir": "जम्मू और कश्मीर",
    "Goa": "गोवा",
    "Puducherry": "पुडुचेरी",
    "Chandigarh": "चंडीगढ़"
  },
  ta: {
    "Delhi": "டெல்லி",
    "Maharashtra": "மகாராஷ்டிரா",
    "Tamil Nadu": "தமிழ்நாடு",
    "Uttar Pradesh": "உத்தரப் பிரதேசம்",
    "West Bengal": "மேற்கு வங்காளம்",
    "Karnataka": "கர்நாடகா",
    "Gujarat": "குஜராத்",
    "Rajasthan": "ராஜஸ்தான்",
    "Punjab": "பஞ்சாப்",
    "Haryana": "ஹரியானா",
    "Kerala": "கேரளா",
    "Madhya Pradesh": "மத்தியப் பிரதேசம்",
    "Telangana": "தெலுங்கானா",
    "Andhra Pradesh": "ஆந்திரப் பிரதேசம்",
    "Odisha": "ஒடிசா",
    "Bihar": "பீகார்",
    "Assam": "அஸ்ஸாம்",
    "Chhattisgarh": "சத்தீஸ்கர்",
    "Jharkhand": "ஜார்க்கண்ட்",
    "Uttarakhand": "உத்தரகாண்ட்",
    "Himachal Pradesh": "இமாச்சலப் பிரதேசம்",
    "Jammu & Kashmir": "ஜம்மு மற்றும் காஷ்மீர்",
    "Goa": "கோவா",
    "Puducherry": "புதுச்சேரி",
    "Chandigarh": "சண்டிகர்"
  }
};

const getRecognitionTypeOptions = (lang: string) => [
  { value: "ALL", label: lang === "hi" ? "सभी मान्यता प्रकार" : lang === "ta" ? "அனைத்து அங்கீகார வகைகள்" : "All Recognition Types" },
  { value: "BIS_RECOGNIZED", label: lang === "hi" ? "बीआईएस मान्यता प्राप्त (LIMS)" : lang === "ta" ? "BIS அங்கீகரிக்கப்பட்டது (LIMS)" : "BIS Recognized (LIMS)" },
  { value: "BIS_EMPANELLED", label: lang === "hi" ? "बीआईएस सूचीबद्ध प्रयोगशाला" : lang === "ta" ? "BIS பட்டியலிடப்பட்ட ஆய்வகம்" : "BIS Empanelled" },
  { value: "BIS_CENTRAL", label: lang === "hi" ? "बीआईएस केंद्रीय शीर्ष प्रयोगशाला" : lang === "ta" ? "BIS மத்திய முதன்மை ஆய்வகம்" : "BIS Central Apex Lab" },
  { value: "BIS_BRANCH", label: lang === "hi" ? "बीआईएस क्षेत्रीय प्रयोगशाला" : lang === "ta" ? "BIS பிராந்திய ஆய்வகம்" : "BIS Regional / Branch Lab" },
  { value: "NABL_ACCREDITED", label: lang === "hi" ? "एनएबीएल मान्यता प्राप्त केंद्र" : lang === "ta" ? "NABL அங்கீகரிக்கப்பட்ட மையம்" : "NABL Accredited Facility" },
];

function LaboratoriesContent() {
  const { t, language } = useLanguage();
  const searchParams = useSearchParams();
  const initialStandard = searchParams.get("standard") || "";
  const initialQuery = searchParams.get("q") || "";

  // State
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [labCodeFilter, setLabCodeFilter] = useState("");
  const [selectedState, setSelectedState] = useState("All States");
  const [standardFilter, setStandardFilter] = useState(initialStandard);
  const [selectedType, setSelectedType] = useState("ALL");
  const [selectedStatus, setSelectedStatus] = useState("ALL");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  // Data & Status
  const [searchResult, setSearchResult] = useState<LaboratorySearchResponse>({
    total_count: 0,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_prev: false,
    laboratories: [],
  });
  const [stats, setStats] = useState<LaboratoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedLabId, setExpandedLabId] = useState<string | null>(null);
  const [availableStates, setAvailableStates] = useState<string[]>([]);

  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  // Sync state when URL searchParams change
  useEffect(() => {
    const std = searchParams.get("standard") || "";
    const q = searchParams.get("q") || "";
    if (std) {
      setStandardFilter((prev) => {
        if (prev !== std) {
          setPage(1);
          return std;
        }
        return prev;
      });
    }
    if (q) {
      setSearchQuery((prev) => {
        if (prev !== q) {
          setPage(1);
          return q;
        }
        return prev;
      });
    }
  }, [searchParams]);

  // Fetch Stats on mount
  useEffect(() => {
    fetchLaboratoryStats()
      .then((data) => {
        setStats(data);
        if (data.states && data.states.length > 0) {
          setAvailableStates(["All States", ...data.states]);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch lab stats:", err);
      });
  }, []);

  // Fetch Labs when filters or page change
  useEffect(() => {
    setLoading(true);
    searchLaboratories({
      query: searchQuery || undefined,
      lab_code: labCodeFilter || undefined,
      state: selectedState === "All States" ? undefined : selectedState,
      standard_number: standardFilter || undefined,
      recognition_type: selectedType === "ALL" ? undefined : selectedType,
      status: selectedStatus === "ALL" ? undefined : selectedStatus,
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_order: sortOrder,
      language,
    })
      .then((res) => {
        setSearchResult(res);
      })
      .catch((err) => {
        console.error("Failed to search laboratories:", err);
        setSearchResult({
          total_count: 0,
          page: 1,
          page_size: pageSize,
          total_pages: 1,
          has_next: false,
          has_prev: false,
          laboratories: [],
        });
      })
      .finally(() => setLoading(false));
  }, [
    searchQuery,
    labCodeFilter,
    selectedState,
    standardFilter,
    selectedType,
    selectedStatus,
    sortBy,
    sortOrder,
    page,
    pageSize,
    language,
  ]);

  const handleResetFilters = () => {
    setSearchQuery("");
    setLabCodeFilter("");
    setSelectedState("All States");
    setStandardFilter("");
    setSelectedType("ALL");
    setSelectedStatus("ALL");
    setSortBy("name");
    setSortOrder("asc");
    setPage(1);
  };

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const QUICK_SECTORS = [
    { label: "⚡ Electrical & Plugs", query: "", standard: "IS 1293" },
    { label: "💻 Electronics & IT", query: "electronics", standard: "IS 13252" },
    { label: "💧 Drinking Water", query: "water", standard: "IS 14543" },
    { label: "🌪️ Fans & Appliances", query: "fan", standard: "IS 17803" },
    { label: "🏗️ TMT Steel & Metals", query: "steel", standard: "IS 1786" },
    { label: "🧱 Cement & Concrete", query: "cement", standard: "IS 269" },
    { label: "☀️ Solar PV & Batteries", query: "solar", standard: "IS 16221" },
  ];

  const getRecognitionBadge = (type: string) => {
    return localizeRecognitionBadge(type, language);
  };

  const isFiltersActive =
    searchQuery ||
    labCodeFilter ||
    selectedState !== "All States" ||
    standardFilter ||
    selectedType !== "ALL" ||
    selectedStatus !== "ALL";

  return (
    <div className="space-y-6 pb-16">
      {/* Header & Stats Banner */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs space-y-5">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-2xl bg-[#071324] text-amber-400 flex items-center justify-center shrink-0">
                <FlaskConical className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
                    {t("laboratories.title", "BIS Laboratory Directory")}
                  </h1>
                  <span className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                    {t("laboratories.badge", "Official LIMS Source")}
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
                  {t(
                    "laboratories.subtitle",
                    "Comprehensive directory of verified BIS recognized, empanelled, and institutional testing facilities across India."
                  )}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl font-medium">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              Last Verified: {stats?.last_imported_at || "2026-10-04"}
            </span>
          </div>
        </div>

        {/* Directory Statistics Grid */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 pt-2 border-t border-slate-100">
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
              <div className="text-slate-500 text-[11px] font-semibold uppercase tracking-wider">
                Total Facilities
              </div>
              <div className="text-xl font-extrabold text-slate-900 mt-0.5">
                {stats.total_laboratories}
              </div>
              <div className="text-[10px] text-slate-500 font-medium mt-0.5">
                {stats.active_count ?? 569} Active · {stats.expired_count ?? 7} Expired
              </div>
            </div>
            <div className="bg-blue-50/50 p-3.5 rounded-xl border border-blue-100">
              <div className="text-bis-blue text-[11px] font-semibold uppercase tracking-wider">
                BIS Recognized
              </div>
              <div className="text-xl font-extrabold text-bis-blue mt-0.5">
                {stats.recognized_count}
              </div>
            </div>
            <div className="bg-amber-50/50 p-3.5 rounded-xl border border-amber-100">
              <div className="text-amber-800 text-[11px] font-semibold uppercase tracking-wider">
                BIS Empanelled
              </div>
              <div className="text-xl font-extrabold text-amber-800 mt-0.5">
                {stats.empaneled_count}
              </div>
            </div>
            <div className="bg-purple-50/50 p-3.5 rounded-xl border border-purple-100">
              <div className="text-purple-800 text-[11px] font-semibold uppercase tracking-wider">
                Institutional / Apex
              </div>
              <div className="text-xl font-extrabold text-purple-800 mt-0.5">
                {stats.institutional_count}
              </div>
            </div>
            <div className="bg-emerald-50/50 p-3.5 rounded-xl border border-emerald-100 col-span-2 sm:col-span-1">
              <div className="text-emerald-800 text-[11px] font-semibold uppercase tracking-wider">
                States & UTs
              </div>
              <div className="text-xl font-extrabold text-emerald-800 mt-0.5">
                {stats.total_states}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Multi-Criteria Filters Card */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
            <Filter className="w-3.5 h-3.5 text-bis-blue" />
            <span>Search & Filter Criteria</span>
          </div>
          {isFiltersActive && (
            <button
              onClick={handleResetFilters}
              className="text-xs font-semibold text-bis-blue hover:text-blue-800 flex items-center gap-1 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              {t("laboratories.reset_filters", "Reset filters")}
            </button>
          )}
        </div>

        {/* Quick Domain Filter Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1.5 scrollbar-none pt-1">
          <span className="text-[11px] font-semibold text-slate-400 shrink-0 mr-1">Quick Sectors:</span>
          {QUICK_SECTORS.map((sec) => {
            const isSecActive =
              (sec.standard && standardFilter === sec.standard) ||
              (sec.query && searchQuery === sec.query);
            return (
              <button
                key={sec.label}
                onClick={() => {
                  if (isSecActive) {
                    setStandardFilter("");
                    setSearchQuery("");
                  } else {
                    setStandardFilter(sec.standard || "");
                    setSearchQuery(sec.query || "");
                  }
                  setPage(1);
                }}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium shrink-0 transition-all border ${
                  isSecActive
                    ? "bg-blue-900 text-white border-blue-900 shadow-xs"
                    : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100 hover:border-slate-300"
                }`}
              >
                {sec.label}
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Keyword Search */}
          <div className="relative lg:col-span-2">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
              placeholder={t(
                "laboratories.search_placeholder",
                "Search by lab name, testing capabilities, city, or address..."
              )}
              className="w-full pl-9 pr-4 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white transition-all text-slate-900 placeholder:text-slate-400 font-medium"
            />
          </div>

          {/* Official Lab Code Filter */}
          <div>
            <input
              type="text"
              value={labCodeFilter}
              onChange={(e) => {
                setLabCodeFilter(e.target.value);
                setPage(1);
              }}
              placeholder="Lab Code (e.g. 8102006)"
              className="w-full px-3 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white transition-all font-mono text-slate-900 placeholder:text-slate-400"
            />
          </div>

          {/* Standard Number Filter */}
          <div>
            <input
              type="text"
              value={standardFilter}
              onChange={(e) => {
                setStandardFilter(e.target.value);
                setPage(1);
              }}
              placeholder={t("laboratories.is_code_placeholder", "IS Standard (e.g. IS 1293)")}
              className="w-full px-3 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white transition-all font-mono text-slate-900 placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Secondary Row Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
          {/* State Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">State / Territory</label>
            <select
              value={selectedState}
              onChange={(e) => {
                setSelectedState(e.target.value);
                setPage(1);
              }}
              className="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-900"
            >
              {(availableStates.length > 0 ? availableStates : ["All States"]).map((st) => {
                const label =
                  st === "All States"
                    ? t("common.all_states", "All States")
                    : STATE_TRANSLATIONS[language]?.[st] || st;
                return (
                  <option key={st} value={st}>
                    {label}
                  </option>
                );
              })}
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Recognition Scheme</label>
            <select
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.target.value);
                setPage(1);
              }}
              className="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-900"
            >
              {getRecognitionTypeOptions(language).map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Status</label>
            <select
              value={selectedStatus}
              onChange={(e) => {
                setSelectedStatus(e.target.value);
                setPage(1);
              }}
              className="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-900"
            >
              <option value="ALL">All Statuses</option>
              <option value="ACTIVE">Active / Valid Recognition</option>
              <option value="EXPIRED">Expired / Due for Renewal</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Sort Results</label>
            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
                className="w-2/3 py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-900"
              >
                <option value="name">Lab Name</option>
                <option value="code">Lab Code</option>
                <option value="state">State & City</option>
                <option value="validity">Validity Date</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                className="w-1/3 py-2 px-2 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl border border-slate-300 transition-colors text-center"
                title="Toggle sort direction"
              >
                {sortOrder === "asc" ? "ASC ↑" : "DESC ↓"}
              </button>
            </div>
          </div>
        </div>

        {/* Filter Summary and Page Size */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-100 text-xs text-slate-600">
          <div>
            Showing{" "}
            <strong className="text-slate-900">
              {searchResult.total_count > 0 ? (searchResult.page - 1) * searchResult.page_size + 1 : 0}
            </strong>{" "}
            -{" "}
            <strong className="text-slate-900">
              {Math.min(searchResult.page * searchResult.page_size, searchResult.total_count)}
            </strong>{" "}
            of <strong className="text-bis-blue">{searchResult.total_count}</strong> verified facilities
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-500">Page Size:</span>
            {[10, 20, 50].map((sz) => (
              <button
                key={sz}
                onClick={() => {
                  setPageSize(sz);
                  setPage(1);
                }}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-colors ${
                  pageSize === sz
                    ? "bg-bis-blue text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {sz}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Lab List / Cards */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm animate-pulse space-y-4">
              <div className="flex justify-between items-center">
                <div className="h-5 bg-slate-200 rounded w-1/3" />
                <div className="h-6 bg-slate-200 rounded-full w-28" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="h-16 bg-slate-100 rounded-xl" />
                <div className="md:col-span-2 h-16 bg-slate-100 rounded-xl" />
              </div>
            </div>
          ))}
        </div>
      ) : searchResult.laboratories.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
          <AlertCircle className="w-10 h-10 text-amber-500 mx-auto" />
          <h2 className="text-base font-bold text-slate-800">
            {t("laboratories.no_match_title", "No matching laboratories found")}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
            {t(
              "laboratories.no_match_desc",
              "No facility matched your current filter criteria. Try clearing the state, lab code, or category filter to view all verified records."
            )}
          </p>
          <button
            onClick={handleResetFilters}
            className="mt-2 inline-flex items-center space-x-1.5 font-bold text-bis-blue bg-blue-50 hover:bg-blue-100 px-4 py-2 rounded-xl transition-colors text-xs"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset all filters</span>
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {searchResult.laboratories.map((lab) => {
            const badge = localizeRecognitionBadge(lab.recognition_type, language);
            const isExpanded = expandedLabId === (lab.id || lab.lab_code);
            const isExpired = lab.status === "EXPIRED";
            const localizedName = localizeLabName(lab.lab_name, language);
            const localizedCity = localizeCity(lab.city, language);
            const localizedState = localizeState(lab.state, language);
            const localizedDistrict = lab.district ? localizeCity(lab.district, language) : "";
            const localizedScope = localizeTestingScope(lab.testing_scope_summary, language);

            return (
              <div
                key={lab.id || lab.lab_code || lab.lab_name}
                className="bg-white p-5 sm:p-6 rounded-2xl border border-slate-200 hover:border-bis-blue shadow-sm hover:shadow-md transition-all space-y-4"
              >
                {/* Card Top: Title, Code, Badges */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-slate-100 pb-3.5">
                  <div className="space-y-1">
                    <div className="flex items-start space-x-2">
                      <Building className="w-4 h-4 text-bis-blue shrink-0 mt-1" />
                      <div>
                        <h2 className="font-bold text-base text-slate-900 leading-snug">
                          {localizedName}
                        </h2>
                        {lab.lab_code && (
                          <div className="flex items-center gap-2 mt-1">
                            <button
                              onClick={() => handleCopyCode(lab.lab_code!)}
                              className="text-[11px] font-mono bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-0.5 rounded-md font-semibold transition-colors flex items-center gap-1"
                              title="Click to copy official lab code"
                            >
                              <span>Lab Code: {lab.lab_code}</span>
                              {copiedCode === lab.lab_code ? (
                                <span className="text-[10px] text-emerald-600 font-bold">✓ Copied</span>
                              ) : null}
                            </button>
                            {lab.district && lab.district.toLowerCase() !== (lab.city || "").toLowerCase() && (
                              <span className="text-[11px] text-slate-500 font-medium">
                                {language === "hi" ? "जिला: " : language === "ta" ? "மாவட்டம்: " : "District: "}
                                {localizedDistrict || lab.district}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 shrink-0">
                    <span
                      className={`text-xs font-bold border px-3 py-1 rounded-full ${badge.className}`}
                    >
                      {badge.label}
                    </span>

                    {lab.validity_date && (
                      <span
                        className={`text-[11px] font-bold px-2.5 py-1 rounded-full border flex items-center gap-1 ${
                          isExpired
                            ? "bg-rose-50 text-rose-700 border-rose-200"
                            : "bg-emerald-50 text-emerald-700 border-emerald-200"
                        }`}
                      >
                        {isExpired ? (
                          <XCircle className="w-3 h-3 text-rose-600" />
                        ) : (
                          <CheckCircle className="w-3 h-3 text-emerald-600" />
                        )}
                        {language === "hi" ? "वैध: " : language === "ta" ? "செல்லுபடியாகும்: " : "Valid: "}
                        {lab.validity_date}
                      </span>
                    )}
                  </div>
                </div>

                {/* Card Body: Address, Contacts, Scope */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs text-slate-600">
                  {/* Location & Contact Information */}
                  <div className="space-y-2.5">
                    <div className="flex items-start space-x-2">
                      <MapPin className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                      <div>
                        <p className="font-bold text-slate-800">
                          {localizedCity}, {localizedState}
                        </p>
                        <p className="text-slate-500 leading-relaxed mt-0.5">
                          {lab.address || `${localizedCity}, ${localizedState}`}
                        </p>
                      </div>
                    </div>

                    {lab.contact_details && (
                      <div className="pt-1.5 space-y-1 bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-slate-600">
                        {lab.contact_details.contact_person && (
                          <div className="font-semibold text-slate-800">
                            👤 {lab.contact_details.contact_person}
                          </div>
                        )}
                        {lab.contact_details.phone && (
                          <div className="flex items-center space-x-2">
                            <Phone className="w-3 h-3 text-slate-400 shrink-0" />
                            <span>{lab.contact_details.phone}</span>
                          </div>
                        )}
                        {lab.contact_details.email && (
                          <div className="flex items-center space-x-2 truncate">
                            <Mail className="w-3 h-3 text-slate-400 shrink-0" />
                            <a
                              href={`mailto:${lab.contact_details.email}`}
                              className="text-bis-blue hover:underline truncate"
                            >
                              {lab.contact_details.email}
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Scope of Testing & Standards */}
                  <div className="lg:col-span-2 space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                        {t("laboratories.testing_scope_title", "Testing Scope & Recognition Profile:")}
                      </p>
                      {lab.scope_url && (
                        <a
                          href={lab.scope_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[11px] font-bold text-bis-blue hover:underline inline-flex items-center gap-1"
                        >
                          {language === "hi"
                            ? "आधिकारिक LIMS दायरा देखें"
                            : language === "ta"
                            ? "அதிகாரப்பூர்வ LIMS நோக்கத்தைக் காண்க"
                            : "View Official LIMS Scope"}{" "}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>

                    <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100 leading-relaxed">
                      {localizedScope ||
                        (language === "hi"
                          ? "बीआईएस एलआईएमएस / प्रयोगशाला मान्यता योजना के तहत मान्यता प्राप्त अनुरूपता परीक्षण एवं गुणवत्ता मूल्यांकन सुविधा।"
                          : language === "ta"
                          ? "BIS LIMS / ஆய்வக அங்கீகாரத் திட்டத்தின் கீழ் அங்கீகரிக்கப்பட்ட இணக்க சோதனை மற்றும் தர மதிப்பீட்டு வசதி."
                          : "Conformity testing and quality evaluation facility recognized under BIS LIMS / Laboratory Recognition Scheme.")}
                    </p>

                    {/* Accredited Standards Badges if present */}
                    {lab.accredited_standards && lab.accredited_standards.length > 0 && (
                      <div className="space-y-1 pt-1">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">
                          {t("laboratories.accredited_standards", "Accredited Indian Standards:")}
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {lab.accredited_standards.map((std) => (
                            <Link
                              key={std}
                              href={`/standards/${encodeURIComponent(std)}`}
                              className="font-mono text-[11px] bg-slate-100 hover:bg-blue-50 text-slate-800 hover:text-bis-blue border border-slate-200 px-2.5 py-0.5 rounded-lg transition-colors font-semibold"
                            >
                              {std}
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Action Footer */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-100 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400">
                      {language === "hi"
                        ? "सत्यापित प्रयोगशाला • स्रोत: "
                        : language === "ta"
                        ? "சரிபார்க்கப்பட்ட ஆய்வகம் • ஆதாரம்: "
                        : "Verified Laboratory • Source: "}
                      <a
                        href={lab.source_url || "https://lims.bis.gov.in/home/labs/"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-600 hover:text-bis-blue underline font-medium"
                      >
                        BIS LIMS
                      </a>
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link
                      href={`/assistant?prompt=${encodeURIComponent(
                        `What products can be tested at ${localizedName} (Lab Code: ${lab.lab_code || "N/A"}) in ${localizedCity}, ${localizedState}?`
                      )}`}
                      className="inline-flex items-center space-x-1.5 font-bold text-bis-blue hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3.5 py-1.5 rounded-xl transition-colors"
                    >
                      <BotMessageSquare className="w-3.5 h-3.5" />
                      <span>{t("laboratories.ask_ai_lab", "Ask AI about this lab")}</span>
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Footer */}
      {searchResult.total_pages > 1 && (
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-600">
            Page <strong className="text-slate-900">{searchResult.page}</strong> of{" "}
            <strong className="text-slate-900">{searchResult.total_pages}</strong> (
            {searchResult.total_count} total facilities)
          </div>

          <div className="flex items-center gap-1.5">
            {/* First Page */}
            <button
              onClick={() => setPage(1)}
              disabled={searchResult.page <= 1}
              className="px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors text-slate-700"
            >
              First
            </button>

            {/* Previous */}
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={!searchResult.has_prev}
              className="px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors text-slate-700 flex items-center gap-1"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              Prev
            </button>

            {/* Page number indicators */}
            {Array.from({ length: Math.min(5, searchResult.total_pages) }, (_, idx) => {
              let pNum = searchResult.page - 2 + idx;
              if (searchResult.page <= 2) pNum = idx + 1;
              if (searchResult.page >= searchResult.total_pages - 2)
                pNum = searchResult.total_pages - 4 + idx;
              if (pNum < 1 || pNum > searchResult.total_pages) return null;

              return (
                <button
                  key={pNum}
                  onClick={() => setPage(pNum)}
                  className={`w-8 h-8 rounded-xl text-xs font-bold transition-colors ${
                    searchResult.page === pNum
                      ? "bg-bis-blue text-white shadow-sm"
                      : "bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200"
                  }`}
                >
                  {pNum}
                </button>
              );
            })}

            {/* Next */}
            <button
              onClick={() => setPage((p) => Math.min(searchResult.total_pages, p + 1))}
              disabled={!searchResult.has_next}
              className="px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors text-slate-700 flex items-center gap-1"
            >
              Next
              <ChevronRight className="w-3.5 h-3.5" />
            </button>

            {/* Last Page */}
            <button
              onClick={() => setPage(searchResult.total_pages)}
              disabled={searchResult.page >= searchResult.total_pages}
              className="px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors text-slate-700"
            >
              Last
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function LaboratoriesPage() {
  const { t } = useLanguage();
  return (
    <Suspense
      fallback={
        <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center text-slate-500 text-sm">
          {t("laboratories.loading_labs", "Loading Laboratories Directory...")}
        </div>
      }
    >
      <LaboratoriesContent />
    </Suspense>
  );
}
