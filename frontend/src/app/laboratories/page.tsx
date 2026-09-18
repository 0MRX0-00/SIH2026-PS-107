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
  AlertCircle
} from "lucide-react";
import { searchLaboratories, LaboratoryItem } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

const INDIAN_STATES = [
  "All States",
  "Delhi",
  "Maharashtra",
  "Tamil Nadu",
  "Uttar Pradesh",
  "West Bengal",
  "Karnataka",
  "Gujarat",
  "Rajasthan",
  "Punjab"
];

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
    "Punjab": "पंजाब"
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
    "Punjab": "பஞ்சாப்"
  }
};

const RECOGNITION_TYPES = [
  "All Recognition Types",
  "BIS_CENTRAL",
  "NABL_ACCREDITED",
  "BIS_BRANCH",
  "BIS_RECOGNIZED"
];

function LaboratoriesContent() {
  const { t, language } = useLanguage();
  const searchParams = useSearchParams();
  const initialStandard = searchParams.get("standard") || "";

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedState, setSelectedState] = useState("All States");
  const [standardFilter, setStandardFilter] = useState(initialStandard);
  const [selectedType, setSelectedType] = useState("All Recognition Types");
  const [labs, setLabs] = useState<LaboratoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    searchLaboratories({
      query: searchQuery || undefined,
      state: selectedState === "All States" ? undefined : selectedState,
      standard_number: standardFilter || undefined,
      recognition_type: selectedType === "All Recognition Types" ? undefined : selectedType,
      language,
    })
      .then((res) => setLabs(res.laboratories))
      .catch((err) => {
        console.error("Failed to load laboratories:", err);
        setLabs([]);
      })
      .finally(() => setLoading(false));
  }, [searchQuery, selectedState, standardFilter, selectedType, language]);

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-5 sm:p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <FlaskConical className="w-5 h-5 text-bis-blue" />
            <h1 className="text-xl font-bold text-slate-900">
              {t("laboratories.title")}
            </h1>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
              {t("laboratories.badge", "Verified Directory")}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {t("laboratories.subtitle")}
          </p>
        </div>

        <div className="text-xs text-slate-600 bg-slate-50 px-3 py-2 rounded-lg border border-slate-200">
          <strong>{labs.length}</strong> {t("laboratories.showing_count")}
        </div>
      </div>

      {/* Multi-Criteria Filters */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Keyword Search */}
          <div className="relative lg:col-span-2">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t("laboratories.search_placeholder", "Search by facility name, testing scope, or city...")}
              className="w-full pl-9 pr-4 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white transition-all text-slate-900 placeholder:text-slate-400"
            />
          </div>

          {/* Standard Number Filter */}
          <div className="relative">
            <input
              type="text"
              value={standardFilter}
              onChange={(e) => setStandardFilter(e.target.value)}
              placeholder={t("laboratories.is_code_placeholder", "Filter by IS Code (e.g. IS 1293)")}
              className="w-full px-3 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white transition-all font-mono text-slate-900 placeholder:text-slate-400"
            />
          </div>

          {/* State Filter */}
          <div>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="w-full py-2.5 px-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-900"
            >
              {INDIAN_STATES.map((st) => {
                const label = st === "All States"
                  ? t("common.all_states", "All States")
                  : (STATE_TRANSLATIONS[language]?.[st] || st);
                return (
                  <option key={st} value={st}>
                    {label}
                  </option>
                );
              })}
            </select>
          </div>
        </div>

        {/* Clear Filters Button */}
        {(searchQuery || selectedState !== "All States" || standardFilter) && (
          <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-500">
            <span>{t("laboratories.filters_active", "Filters active")}</span>
            <button
              onClick={() => {
                setSearchQuery("");
                setSelectedState("All States");
                setStandardFilter("");
              }}
              className="font-bold text-bis-blue hover:underline"
            >
              {t("laboratories.reset_filters", "Reset all filters")}
            </button>
          </div>
        )}
      </div>

      {/* Lab List / Cards */}
      {loading ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center space-y-2">
          <div className="w-8 h-8 border-4 border-bis-blue border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs font-semibold text-slate-500">{t("laboratories.searching", "Searching accredited laboratories...")}</p>
        </div>
      ) : labs.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center space-y-2">
          <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />
          <p className="font-bold text-slate-800">{t("laboratories.no_match_title", "No matching laboratories found")}</p>
          <p className="text-xs text-slate-500">
            {t("laboratories.no_match_desc", "Try adjusting state or standard filters. All laboratory records are strictly verified to prevent hallucination.")}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {labs.map((lab) => (
            <div
              key={lab.id || lab.lab_name}
              className="bg-white p-6 rounded-2xl border border-slate-200 hover:border-bis-blue shadow-sm hover:shadow transition-all space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <Building className="w-4 h-4 text-bis-blue" />
                    <h2 className="font-bold text-base text-slate-900">{lab.lab_name}</h2>
                  </div>
                  {lab.lab_code && (
                    <span className="text-[11px] font-mono text-slate-500">
                      {t("laboratories.code_label", "Code:")} {lab.lab_code}
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold bg-blue-50 text-bis-blue border border-blue-200 px-3 py-1 rounded-full">
                    {lab.recognition_type.replace(/_/g, " ")}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs text-slate-600">
                {/* Location & Address */}
                <div className="space-y-2">
                  <div className="flex items-start space-x-2">
                    <MapPin className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-slate-800">{lab.city}, {lab.state}</p>
                      <p className="text-slate-500 leading-relaxed">{lab.address}</p>
                    </div>
                  </div>

                  {lab.contact_details && (
                    <div className="pt-1 space-y-1 text-slate-500">
                      {lab.contact_details.phone && (
                        <div className="flex items-center space-x-2">
                          <Phone className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span>{lab.contact_details.phone}</span>
                        </div>
                      )}
                      {lab.contact_details.email && (
                        <div className="flex items-center space-x-2">
                          <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span>{lab.contact_details.email}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Scope of Testing */}
                <div className="lg:col-span-2 space-y-2">
                  <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                    {t("laboratories.testing_scope_title", "Testing Scope & Capabilities:")}
                  </p>
                  <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-100 leading-relaxed">
                    {lab.testing_scope_summary || t("laboratories.general_scope", "General conformity testing as per accredited Indian Standards.")}
                  </p>

                  {/* Accredited Standards Badges */}
                  {lab.accredited_standards && lab.accredited_standards.length > 0 && (
                    <div className="space-y-1 pt-1">
                      <p className="text-[10px] font-bold text-slate-500 uppercase">{t("laboratories.accredited_standards", "Accredited IS Standards:")}</p>
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

              {/* Action Footer */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-100 text-xs">
                <span className="text-slate-500">
                  {t("laboratories.verified_facility", "Accredited facility verified under BIS Conformity Assessment Regulations.")}
                </span>

                <Link
                  href={`/assistant?prompt=${encodeURIComponent(`What tests can ${lab.lab_name} perform and what is the sample submission procedure?`)}`}
                  className="inline-flex items-center space-x-1.5 font-bold text-bis-blue hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-xl transition-colors"
                >
                  <BotMessageSquare className="w-3.5 h-3.5" />
                  <span>{t("laboratories.ask_ai_lab", "Ask AI about {labName}").replace("{labName}", lab.lab_name)}</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function LaboratoriesPage() {
  const { t } = useLanguage();
  return (
    <Suspense fallback={<div className="bg-white p-12 rounded-xl border border-slate-200 text-center text-slate-500 text-sm">{t("laboratories.loading_labs", "Loading Laboratories Directory...")}</div>}>
      <LaboratoriesContent />
    </Suspense>
  );
}
