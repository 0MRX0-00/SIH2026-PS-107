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
  Award
} from "lucide-react";
import { getStandardDetails, StandardDetailResponse } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

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

  useEffect(() => {
    if (!decodedNumber) return;
    setLoading(true);
    getStandardDetails(decodedNumber, language)
      .then((data) => {
        setStandard(data);
        // Expand first clause by default
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
      <div className="bg-white p-12 rounded-xl border border-slate-200 text-center space-y-3">
        <div className="w-8 h-8 border-4 border-bis-blue border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-600">
          {t("standards_detail.loading_details", "Retrieving details for {standardNumber}...").replace("{standardNumber}", decodedNumber)}
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
          <span>{t("standards_detail.back_to_standards", "Back to Standards Explorer")}</span>
        </button>
        <div className="bg-white p-10 rounded-xl border border-red-200 text-center space-y-3">
          <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
          <h2 className="text-lg font-bold text-slate-800">{t("standards_detail.not_found_title", "Standard Not Found")}</h2>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            {t("standards_detail.not_found_desc", "The standard '{standardNumber}' could not be retrieved from the verified repository.").replace("{standardNumber}", decodedNumber)}
          </p>
          <Link
            href="/standards"
            className="inline-block bg-bis-blue text-white font-bold text-xs px-4 py-2 rounded-lg"
          >
            {t("standards_detail.explore_catalogue", "Explore Standards Catalogue")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/standards"
          className="inline-flex items-center text-xs font-bold text-slate-600 hover:text-bis-blue space-x-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t("standards_detail.back_to_standards", "Back to Standards Explorer")}</span>
        </Link>

        <div className="flex items-center space-x-2">
          <Link
            href={`/certification?standard=${encodeURIComponent(standard.standard_number)}`}
            className="inline-flex items-center text-xs font-bold text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 px-3 py-1.5 rounded-lg space-x-1 transition-colors"
          >
            <Award className="w-3.5 h-3.5" />
            <span>{t("standards_detail.cert_roadmap_btn", "Certification Roadmap")}</span>
          </Link>
          <Link
            href={`/laboratories?standard=${encodeURIComponent(standard.standard_number)}`}
            className="inline-flex items-center text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 px-3 py-1.5 rounded-lg space-x-1 transition-colors"
          >
            <FlaskConical className="w-3.5 h-3.5" />
            <span>{t("standards_detail.find_labs_btn", "Find Testing Labs")}</span>
          </Link>
        </div>
      </div>

      {/* Main Standard Header Card */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4 relative overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <span className="font-mono text-base sm:text-lg font-extrabold text-white bg-bis-navy px-3.5 py-1 rounded-lg">
              {standard.standard_number}
            </span>
            <span className="text-xs font-bold px-2.5 py-1 rounded bg-slate-100 text-slate-700 uppercase">
              {standard.status}
            </span>
          </div>

          <div>
            {standard.is_qco_mandatory ? (
              <span className="inline-flex items-center text-xs font-bold text-red-700 bg-red-50 border border-red-200 px-3 py-1 rounded-full">
                <AlertTriangle className="w-3.5 h-3.5 mr-1.5 text-red-600" />
                {t("common.mandatory_qco", "Mandatory Quality Control Order (QCO)")}
              </span>
            ) : (
              <span className="inline-flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
                <CheckCircle className="w-3.5 h-3.5 mr-1.5 text-emerald-600" />
                {t("common.voluntary", "Voluntary Standard")}
              </span>
            )}
          </div>
        </div>

        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 leading-snug">
          {standard.title}
        </h1>

        {/* Metadata Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg flex items-center space-x-3">
            <Building2 className="w-5 h-5 text-bis-blue shrink-0" />
            <div>
              <p className="text-[10px] font-semibold text-slate-500 uppercase">{t("standards_detail.technical_division", "Technical Division")}</p>
              <p className="text-xs font-bold text-slate-800">{standard.division}</p>
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg flex items-center space-x-3">
            <Calendar className="w-5 h-5 text-bis-blue shrink-0" />
            <div>
              <p className="text-[10px] font-semibold text-slate-500 uppercase">{t("standards_detail.year_edition", "Year / Edition")}</p>
              <p className="text-xs font-bold text-slate-800">{standard.year || t("standards_detail.current_edition", "Current Edition")}</p>
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-100 p-3 rounded-lg flex items-center space-x-3">
            <Layers className="w-5 h-5 text-bis-blue shrink-0" />
            <div>
              <p className="text-[10px] font-semibold text-slate-500 uppercase">{t("standards_detail.clauses_indexed", "Clause Sections Indexed")}</p>
              <p className="text-xs font-bold text-slate-800">{standard.sections.length} {t("standards_detail.clauses_count_suffix", "Clauses")}</p>
            </div>
          </div>
        </div>

        {/* Mandatory QCO Order Details if applicable */}
        {standard.is_qco_mandatory && standard.qco_order_number && (
          <div className="bg-red-50/70 border border-red-200 rounded-xl p-4 text-xs space-y-1">
            <div className="flex items-center space-x-2 text-red-900 font-bold">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <span>{t("standards_detail.qco_title", "Gazetted Quality Control Order")}</span>
            </div>
            <p className="text-red-800 leading-relaxed">
              {t("standards_detail.qco_notice", "Order: {orderNumber}. Manufacture, import, distribution, or sale of products without a valid BIS standard mark under this order is prohibited under the BIS Act, 2016.").replace("{orderNumber}", standard.qco_order_number)}
            </p>
          </div>
        )}

        {/* Primary Action Button: Ask Sahayak */}
        <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <p className="text-xs text-slate-500">
            {t("standards_detail.question_prompt", "Have a question regarding testing limits, ratings, or scope of this standard?")}
          </p>
          <Link
            href={`/assistant?standard=${encodeURIComponent(standard.standard_number)}&prompt=${encodeURIComponent(`Explain key specifications and clauses for ${standard.standard_number}`)}`}
            className="bg-bis-saffron hover:bg-bis-saffronDark text-slate-950 font-bold px-5 py-2.5 rounded-xl text-xs sm:text-sm transition-all shadow-sm flex items-center justify-center space-x-2 shrink-0"
          >
            <BotMessageSquare className="w-4 h-4" />
            <span>{t("standards_detail.ask_sahayak_btn", "Ask Sahayak about {standardNumber}").replace("{standardNumber}", standard.standard_number)}</span>
          </Link>
        </div>
      </div>

      {/* Scope Overview */}
      {standard.scope_summary && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <BookOpen className="w-4 h-4 text-bis-blue" />
            <span>{t("standards_detail.scope_title", "Standard Scope & Applicability")}</span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
            {standard.scope_summary}
          </p>
        </div>
      )}

      {/* Clause Tree / Hierarchy */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Layers className="w-5 h-5 text-bis-blue" />
            <span>{t("standards_detail.clauses_title", "Clauses & Technical Sections")}</span>
          </h2>
          <span className="text-xs text-slate-500 font-medium">
            {standard.sections.length} {t("standards_detail.clauses_ingested_count", "Clauses Ingested")}
          </span>
        </div>

        {standard.sections.length === 0 ? (
          <p className="text-xs text-slate-500 italic">{t("standards_detail.no_clauses", "No clause extracts available for this standard.")}</p>
        ) : (
          <div className="space-y-3">
            {standard.sections.map((sec) => {
              const isExpanded = !!expandedClauses[sec.clause_number];
              return (
                <div
                  key={sec.clause_number}
                  className="border border-slate-200 rounded-xl overflow-hidden transition-all"
                >
                  <button
                    onClick={() => toggleClause(sec.clause_number)}
                    className="w-full bg-slate-50 hover:bg-slate-100 p-4 text-left flex items-center justify-between transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="font-mono text-xs font-bold text-bis-blue bg-white border border-blue-200 px-2 py-0.5 rounded">
                        {t("standards_detail.clause_label", "Clause")} {sec.clause_number}
                      </span>
                      <span className="text-xs sm:text-sm font-bold text-slate-800">
                        {sec.clause_title || t("standards_detail.technical_provision", "Technical Provision")}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 text-slate-500">
                      {sec.page_number && (
                        <span className="text-[10px] font-semibold bg-white px-2 py-0.5 rounded border border-slate-200">
                          {t("standards_detail.page_label", "Page")} {sec.page_number}
                        </span>
                      )}
                      {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="p-4 bg-white border-t border-slate-100 space-y-3">
                      <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-sans whitespace-pre-wrap">
                        {sec.content}
                      </p>
                      <div className="flex justify-end pt-2">
                        <Link
                          href={`/assistant?standard=${encodeURIComponent(standard.standard_number)}&prompt=${encodeURIComponent(`What does Clause ${sec.clause_number} (${sec.clause_title || ""}) in ${standard.standard_number} require?`)}`}
                          className="text-[11px] font-bold text-bis-blue hover:text-blue-800 flex items-center space-x-1"
                        >
                          <BotMessageSquare className="w-3.5 h-3.5" />
                          <span>{t("standards_detail.ask_ai_clause", "Ask AI about Clause {clauseNumber}").replace("{clauseNumber}", sec.clause_number)}</span>
                        </Link>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Related Standards */}
      {standard.related_standards && standard.related_standards.length > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h2 className="text-sm font-bold text-slate-900">{t("standards_detail.related_standards", "Related Standards & Harmonized Norms")}</h2>
          <div className="flex flex-wrap gap-2">
            {standard.related_standards.map((rel) => (
              <span
                key={rel}
                className="font-mono text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-200 px-3 py-1 rounded-lg"
              >
                {rel}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
