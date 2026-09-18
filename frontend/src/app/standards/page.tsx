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
  BotMessageSquare
} from "lucide-react";
import { listStandards, StandardListItem } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

const TECHNICAL_DIVISIONS = [
  "All Technical Divisions",
  "Electrotechnical",
  "Electronics & Information Technology",
  "Food and Agriculture",
  "Civil Engineering",
  "Mechanical Engineering",
  "Chemical"
];

const DIVISION_TRANSLATIONS: Record<string, Record<string, string>> = {
  hi: {
    "Electrotechnical": "इलेक्ट्रो-तकनीकी",
    "Electronics & Information Technology": "इलेक्ट्रॉनिक्स और सूचना प्रौद्योगिकी",
    "Food and Agriculture": "खाद्य और कृषि",
    "Civil Engineering": "सिविल इंजीनियरिंग",
    "Mechanical Engineering": "मैकेनिकल इंजीनियरिंग",
    "Chemical": "केमिकल (रसायन)"
  },
  ta: {
    "Electrotechnical": "மின் தொழில்நுட்பம்",
    "Electronics & Information Technology": "மின்னணுவியல் & தகவல் தொழில்நுட்பம்",
    "Food and Agriculture": "உணவு மற்றும் விவசாயம்",
    "Civil Engineering": "கட்டுமானப் பொறியியல்",
    "Mechanical Engineering": "இயந்திரப் பொறியியல்",
    "Chemical": "வேதியியல்"
  }
};

export default function StandardsExplorerPage() {
  const { t, language } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDivision, setSelectedDivision] = useState("All Technical Divisions");
  const [qcoOnly, setQcoOnly] = useState(false);
  const [standards, setStandards] = useState<StandardListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const divFilter = selectedDivision === "All Technical Divisions" ? undefined : selectedDivision;
    listStandards({
      q: searchQuery || undefined,
      division: divFilter,
      qco_only: qcoOnly ? true : undefined,
      language,
    })
      .then((data) => setStandards(data))
      .catch((err) => {
        console.error("Failed to load standards:", err);
        setStandards([]);
      })
      .finally(() => setIsLoading(false));
  }, [searchQuery, selectedDivision, qcoOnly, language]);

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-5 sm:p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <FileSearch className="w-5 h-5 text-bis-blue" />
            <h1 className="text-xl font-bold text-slate-900">
              {t("standards.title")}
            </h1>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
              {t("standards.badge", "National Repository")}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {t("standards.subtitle")}
          </p>
        </div>

        <div className="text-xs text-slate-600 bg-slate-50 px-3 py-2 rounded-lg border border-slate-200">
          <strong>{standards.length}</strong> {t("standards.showing_count")}
        </div>
      </div>

      {/* Search & Filter Controls */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t("standards.search_placeholder")}
              className="w-full pl-9 pr-4 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white transition-all text-slate-900 placeholder:text-slate-400"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400 shrink-0" />
            <select
              value={selectedDivision}
              onChange={(e) => setSelectedDivision(e.target.value)}
              className="w-full py-2 px-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-900"
            >
              {TECHNICAL_DIVISIONS.map((div) => {
                const label = div === "All Technical Divisions"
                  ? t("common.all_divisions")
                  : (DIVISION_TRANSLATIONS[language]?.[div] || div);
                return (
                  <option key={div} value={div}>
                    {label}
                  </option>
                );
              })}
            </select>
          </div>
        </div>

        {/* Filters and Toggle */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 text-xs">
          <div className="flex items-center space-x-3">
            <label className="flex items-center space-x-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={qcoOnly}
                onChange={(e) => setQcoOnly(e.target.checked)}
                className="rounded text-bis-blue focus:ring-bis-blue"
              />
              <span className="font-semibold text-slate-700">{t("standards.qco_filter")}</span>
            </label>
          </div>

          <div className="text-slate-500">
            {t("standards.click_info", "Click on any standard to view clauses, scope, and ask AI questions.")}
          </div>
        </div>
      </div>

      {/* Standards List / Cards */}
      {isLoading ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center text-slate-500 text-sm">
          {t("standards.loading", "Loading standards catalogue...")}
        </div>
      ) : standards.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center space-y-2">
          <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto" />
          <p className="font-bold text-slate-800">{t("standards.no_match_title", "No matching Indian Standards found")}</p>
          <p className="text-xs text-slate-500">{t("standards.no_match_desc", "Try adjusting your keyword or division filter.")}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {standards.map((std) => (
            <div
              key={std.id || std.standard_number}
              className="bg-white p-5 rounded-xl border border-slate-200 hover:border-bis-blue shadow-sm hover:shadow transition-all space-y-3"
            >
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex items-center space-x-3">
                  <span className="font-mono text-sm font-extrabold text-bis-blue bg-blue-50 px-2.5 py-1 rounded border border-blue-200">
                    {std.standard_number}
                  </span>
                  {std.year && (
                    <span className="text-xs font-semibold text-slate-500">
                      {t("standards.year_label", "Year:")} {std.year}
                    </span>
                  )}
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700 uppercase">
                    {std.status}
                  </span>
                </div>

                <div>
                  {std.is_qco_mandatory ? (
                    <span className="inline-flex items-center text-xs font-bold text-red-700 bg-red-50 border border-red-200 px-2.5 py-0.5 rounded-full">
                      <AlertTriangle className="w-3 h-3 mr-1 text-red-600" />
                      {t("common.mandatory_qco")}
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                      <CheckCircle className="w-3 h-3 mr-1 text-emerald-600" />
                      {t("common.voluntary")}
                    </span>
                  )}
                </div>
              </div>

              <div>
                <h2 className="text-base font-bold text-slate-900 leading-snug">
                  {std.title}
                </h2>
                <div className="flex items-center space-x-2 text-xs text-slate-500 mt-1">
                  <Building2 className="w-3.5 h-3.5 text-slate-400" />
                  <span>{t("standards.division_label", "Division:")} <strong>{std.division}</strong></span>
                </div>
              </div>

              {std.scope_summary && (
                <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100 leading-relaxed">
                  {std.scope_summary}
                </p>
              )}

              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 text-xs">
                <div className="flex items-center space-x-2">
                  <Link
                    href={`/assistant?standard=${encodeURIComponent(std.standard_number)}&prompt=${encodeURIComponent(`Explain the core scope and testing requirements for ${std.standard_number}`)}`}
                    className="inline-flex items-center space-x-1 text-bis-blue hover:text-blue-800 font-bold bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <BotMessageSquare className="w-3.5 h-3.5" />
                    <span>{t("standards.ask_about")} {std.standard_number}</span>
                  </Link>
                </div>

                <Link
                  href={`/standards/${encodeURIComponent(std.standard_number)}`}
                  className="inline-flex items-center space-x-1 font-bold text-slate-700 hover:text-slate-900 px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 transition-colors"
                >
                  <span>{t("standards.view_clauses")}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
