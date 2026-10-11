"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileText,
  ShieldCheck,
  AlertTriangle,
  CheckCircle,
  Building2,
  Calendar,
  Layers,
  ArrowLeft,
  BotMessageSquare,
  Sparkles,
  BookOpen,
  ChevronDown,
  ChevronRight,
  FlaskConical,
  Award,
  ExternalLink,
} from "lucide-react";
import { getStandardDetails, StandardDetailResponse } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import { localizeStandard } from "@/lib/localizeStandards";

export default function StandardDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { t, language } = useLanguage();
  const standardNumberParam = params.standardNumber as string;
  const decodedNumber = decodeURIComponent(standardNumberParam || "");

  const [standard, setStandard] = useState<StandardDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedClauses, setExpandedClauses] = useState<Record<string, boolean>>({});

  const loc = standard
    ? localizeStandard(
        standard.standard_number,
        standard.title,
        standard.scope_summary,
        standard.division,
        language
      )
    : { title: "", scope: "", division: "", number: "" };

  useEffect(() => {
    if (!decodedNumber) return;
    setLoading(true);
    getStandardDetails(decodedNumber, language)
      .then((data) => {
        setStandard(data);
        if (data.sections && data.sections.length > 0) {
          setExpandedClauses({ [data.sections[0].clause_number]: true });
        }
      })
      .catch((err) => {
        setError(err.message || "Failed to load standard details");
      })
      .finally(() => setLoading(false));
  }, [decodedNumber, language]);

  const toggleClause = (clauseNum: string) => {
    setExpandedClauses((prev) => ({ ...prev, [clauseNum]: !prev[clauseNum] }));
  };

  if (loading) {
    return (
      <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3 shadow-xs">
        <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-700">
          Retrieving standard specification for {decodedNumber}...
        </p>
      </div>
    );
  }

  if (error || !standard) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center text-xs font-bold text-slate-600 hover:text-slate-900 space-x-1"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Standards Explorer</span>
        </button>
        <div className="bg-white p-10 rounded-3xl border border-rose-200 text-center space-y-3">
          <p className="text-sm font-bold text-rose-700">
            {error || `Standard '${decodedNumber}' not found in registry.`}
          </p>
          <Link
            href="/standards"
            className="inline-block bg-[#071324] text-white text-xs font-bold px-4 py-2 rounded-xl"
          >
            Browse Verified Standards
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Navigation & Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center space-x-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 px-3.5 py-2 rounded-xl shadow-xs transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>{t("standards_detail.back_to_standards", "Back to Standards")}</span>
        </button>

        <Link
          href={`/assistant?prompt=${encodeURIComponent(
            `Explain the technical clauses and compliance criteria for ${standard.standard_number}`
          )}`}
          className="inline-flex items-center space-x-1.5 text-xs font-bold text-slate-950 bg-amber-500 hover:bg-amber-400 px-3.5 py-2 rounded-xl shadow-xs transition-colors"
        >
          <BotMessageSquare className="w-3.5 h-3.5" />
          <span>{t("standards.ask_about", "Ask AI about")} {loc.number || standard.standard_number}</span>
        </Link>
      </div>

      {/* Main Standard Overview Card */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono font-black text-lg sm:text-xl text-[#071324] bg-slate-100 px-3 py-1 rounded-xl border border-slate-200">
                {loc.number || standard.standard_number}
              </span>
              {standard.is_qco_mandatory ? (
                <span className="text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300 px-2.5 py-1 rounded-full flex items-center space-x-1">
                  <AlertTriangle className="w-3 h-3" />
                  <span>{t("standards.qco_mandatory", "Mandatory Quality Control Order (QCO)")}</span>
                </span>
              ) : (
                <span className="text-xs font-bold bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full">
                  {t("standards.voluntary", "Voluntary Standard")}
                </span>
              )}
            </div>

            <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] leading-tight">
              {loc.title || standard.title}
            </h1>
          </div>

          {standard.source_url && (
            <a
              href={standard.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1.5 text-xs font-bold text-blue-700 hover:text-blue-900 bg-blue-50 border border-blue-200 px-3 py-2 rounded-xl shrink-0"
            >
              <span>{t("standards.official_catalogue", "Official BIS Gazette / Portal")}</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>

        {/* Metadata Details Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-2xl">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              {t("standards_detail.technical_division", "Technical Division")}
            </span>
            <p className="font-bold text-xs text-slate-800 mt-1 truncate">
              {loc.division || standard.division}
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-2xl">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Committee Code
            </span>
            <p className="font-bold text-xs text-slate-800 mt-1 truncate">
              {standard.technical_committee || "Sectional Committee"}
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-2xl">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              {t("standards_detail.year_edition", "Year / Edition")}
            </span>
            <p className="font-bold text-xs text-slate-800 mt-1">
              {standard.year || t("standards_detail.current_edition", "Current Edition")}
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-2xl">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Verification Status
            </span>
            <p className="font-bold text-xs text-emerald-700 mt-1 flex items-center space-x-1">
              <CheckCircle className="w-3 h-3" />
              <span>Authoritative</span>
            </p>
          </div>
        </div>

        {/* Scope Summary */}
        {(loc.scope || standard.scope_summary) && (
          <div className="p-4 bg-slate-50/70 border border-slate-200 rounded-2xl space-y-1.5">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Scope & Applicability
            </h3>
            <p className="text-xs text-slate-700 leading-relaxed">
              {loc.scope || standard.scope_summary}
            </p>
          </div>
        )}

        {/* Technical Clauses Breakdown */}
        {standard.sections && standard.sections.length > 0 && (
          <div className="space-y-3 pt-4 border-t border-slate-100">
            <h3 className="font-bold text-sm text-[#0F172A] flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-amber-600" />
              <span>Technical Clauses & Requirement Breakdown ({standard.sections.length})</span>
            </h3>

            <div className="space-y-2">
              {standard.sections.map((sec, idx) => {
                const isExpanded = expandedClauses[sec.clause_number];
                return (
                  <div
                    key={idx}
                    className="border border-slate-200 rounded-2xl overflow-hidden transition-all"
                  >
                    <button
                      onClick={() => toggleClause(sec.clause_number)}
                      className="w-full text-left p-3.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-xs font-bold text-slate-900 transition-colors"
                    >
                      <div className="flex items-center space-x-2.5">
                        <span className="font-mono bg-white px-2 py-0.5 rounded-md border border-slate-200 text-blue-900">
                          Clause {sec.clause_number}
                        </span>
                        <span>{sec.clause_title || "Technical Requirement"}</span>
                      </div>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      )}
                    </button>

                    {isExpanded && (
                      <div className="p-4 bg-white text-xs text-slate-700 leading-relaxed border-t border-slate-200">
                        <p className="whitespace-pre-wrap">{sec.content}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
