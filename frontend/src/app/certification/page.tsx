"use client";

import React, { useState, useEffect, Suspense } from "react";
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
  Info
} from "lucide-react";
import {
  generateCertificationRoadmap,
  listCertificationSchemes,
  CertificationRoadmapResponse,
  CertificationScheme
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

function CertificationContent() {
  const { t, language } = useLanguage();
  const searchParams = useSearchParams();
  const initialStandard = searchParams.get("standard") || "";

  const [productInput, setProductInput] = useState(initialStandard || "IS 1293:2019");
  const [activeRoadmap, setActiveRoadmap] = useState<CertificationRoadmapResponse | null>(null);
  const [schemes, setSchemes] = useState<CertificationScheme[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"wizard" | "schemes">("wizard");

  const loadRoadmap = (query: string, lang?: string) => {
    if (!query.trim()) return;
    setLoading(true);
    generateCertificationRoadmap({
      product_name: query.trim(),
      standard_number: query.includes("IS") ? query.trim() : undefined,
      language: lang || language,
    })
      .then((data) => setActiveRoadmap(data))
      .catch((err) => console.error("Roadmap generation failed:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    listCertificationSchemes(language)
      .then((data) => setSchemes(data))
      .catch((err) => console.error("Failed to load schemes:", err));
  }, [language]);

  useEffect(() => {
    loadRoadmap(productInput, language);
  }, [language]);

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    loadRoadmap(productInput, language);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-5 sm:p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-bis-blue" />
            <h1 className="text-xl font-bold text-slate-900">
              {t("certification.title")}
            </h1>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
              {t("certification.badge", "Official Schemes")}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {t("certification.subtitle")}
          </p>
        </div>

        {/* Tab Toggle */}
        <div className="flex bg-slate-100 p-1 rounded-lg text-xs font-semibold">
          <button
            onClick={() => setActiveTab("wizard")}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === "wizard" ? "bg-white text-bis-navy shadow-sm" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            {t("certification.wizard_tab")}
          </button>
          <button
            onClick={() => setActiveTab("schemes")}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === "schemes" ? "bg-white text-bis-navy shadow-sm" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            {t("certification.schemes_tab")}
          </button>
        </div>
      </div>

      {activeTab === "wizard" && (
        <div className="space-y-6">
          {/* Interactive Roadmap Search & Product Bar */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="space-y-1">
              <h2 className="text-sm font-bold text-slate-900">
                {t("certification.generate_title", "Generate Custom Certification Roadmap")}
              </h2>
              <p className="text-xs text-slate-500">
                {t("certification.generate_desc", "Enter your product name or Indian Standard number:")}
              </p>
            </div>

            <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                <input
                  type="text"
                  value={productInput}
                  onChange={(e) => setProductInput(e.target.value)}
                  placeholder={t("certification.input_placeholder", "e.g. Plugs and Sockets (IS 1293:2019)...")}
                  className="w-full pl-9 pr-4 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white transition-all"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-bis-navy hover:bg-slate-800 text-white font-bold px-6 py-2.5 rounded-xl text-xs sm:text-sm transition-all shadow-sm flex items-center justify-center space-x-2 shrink-0 disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4 text-bis-saffron" />
                <span>{loading ? t("certification.generating_btn", "Generating...") : t("certification.generate_btn", "Generate Roadmap")}</span>
              </button>
            </form>

            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-500">
              <span className="font-medium">{t("certification.quick_examples", "Quick examples:")}</span>
              {["IS 1293:2019 Plugs", "IS 13252 IT Equipment", "IS 17803 Ceiling Fans", "Packaged Drinking Water"].map((item) => (
                <button
                  key={item}
                  onClick={() => {
                    setProductInput(item);
                    loadRoadmap(item);
                  }}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1 rounded-lg border border-slate-200 transition-colors"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {/* Active Roadmap Visualizer */}
          {activeRoadmap && (
            <div className="space-y-6">
              {/* Product & Scheme Header Card */}
              <div className="bg-gradient-to-r from-slate-900 to-bis-navy text-white p-6 sm:p-7 rounded-2xl border border-slate-800 shadow-md space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-bis-saffron bg-bis-saffron/20 border border-bis-saffron/30 px-2.5 py-0.5 rounded-full">
                      {activeRoadmap.applicable_scheme || "SCHEME_I_ISI"}
                    </span>
                    {activeRoadmap.is_mandatory_qco && (
                      <span className="text-xs font-bold text-red-300 bg-red-900/50 border border-red-500/40 px-2.5 py-0.5 rounded-full">
                        {t("certification.qco_enforced", "Mandatory QCO Enforced")}
                      </span>
                    )}
                  </div>

                  {activeRoadmap.standard_number && (
                    <Link
                      href={`/standards/${encodeURIComponent(activeRoadmap.standard_number)}`}
                      className="text-xs font-mono font-bold text-blue-300 hover:underline flex items-center space-x-1"
                    >
                      <span>{t("certification.standard_link", "Standard:")} {activeRoadmap.standard_number}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  )}
                </div>

                <h2 className="text-xl sm:text-2xl font-bold leading-tight">
                  {t("certification.pathway_title", "Certification Pathway:")} {activeRoadmap.product}
                </h2>
                <p className="text-xs sm:text-sm text-slate-300">
                  {t("certification.applicable_process", "Applicable Process:")} <strong>{activeRoadmap.scheme_name || "Scheme-I Product Certification (ISI Mark)"}</strong>
                </p>
              </div>

              {/* 5-Step Visual Stepper */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-bis-blue" />
                  <span>{t("certification.roadmap_title", "5-Stage Compliance Roadmap")}</span>
                </h3>

                <div className="grid grid-cols-1 gap-4">
                  {activeRoadmap.steps.map((step) => (
                    <div
                      key={step.step_number}
                      className="bg-white p-5 sm:p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-bis-blue transition-all space-y-3 relative overflow-hidden"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-bis-navy text-white text-xs font-extrabold flex items-center justify-center shrink-0">
                            {step.step_number}
                          </div>
                          <h4 className="font-bold text-slate-900 text-sm sm:text-base">
                            {step.title}
                          </h4>
                        </div>

                        {step.status_badge && (
                          <span className="text-[11px] font-bold text-bis-blue bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full self-start sm:self-auto">
                            {step.status_badge}
                          </span>
                        )}
                      </div>

                      <p className="text-xs sm:text-sm text-slate-600 leading-relaxed pl-0 sm:pl-11">
                        {step.description}
                      </p>

                      {step.checklist && step.checklist.length > 0 && (
                        <div className="pl-0 sm:pl-11 pt-2 space-y-1.5">
                          <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                            {t("certification.action_items", "Action Items & Documentation:")}
                          </p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {step.checklist.map((item, idx) => (
                              <div
                                key={idx}
                                className="flex items-start space-x-2 text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-100"
                              >
                                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                                <span>{item}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Disclaimer Notice Banner */}
              <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-xs text-amber-900 flex items-start space-x-3">
                <Info className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="font-bold">{t("certification.disclaimer_title", "Official Disclaimer & Safety Advisory")}</p>
                  <p className="leading-relaxed text-amber-800">
                    {activeRoadmap.disclaimer}
                  </p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                <Link
                  href={`/laboratories?standard=${encodeURIComponent(activeRoadmap.standard_number || "")}`}
                  className="bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 font-bold px-4 py-2 rounded-xl text-xs flex items-center space-x-2 transition-colors"
                >
                  <FlaskConical className="w-4 h-4" />
                  <span>{t("certification.find_labs_btn", "Find Recognized Labs for this Standard")}</span>
                </Link>

                <Link
                  href={`/assistant?prompt=${encodeURIComponent(`How do I apply for BIS certification for ${activeRoadmap.product}? What are the fees and testing steps?`)}`}
                  className="bg-bis-saffron hover:bg-bis-saffronDark text-slate-950 font-bold px-4 py-2 rounded-xl text-xs flex items-center space-x-2 transition-colors shadow-sm"
                >
                  <BotMessageSquare className="w-4 h-4" />
                  <span>{t("certification.ask_workflow_btn", "Ask Sahayak about this Workflow")}</span>
                </Link>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "schemes" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {schemes.map((scheme) => (
            <div
              key={scheme.scheme_code}
              className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-bis-blue transition-all space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <span className="font-mono text-xs font-bold text-bis-blue bg-blue-50 px-2.5 py-1 rounded-md border border-blue-200 inline-block">
                  {scheme.scheme_code}
                </span>

                <h3 className="font-bold text-slate-900 text-base leading-snug">
                  {scheme.name}
                </h3>

                <p className="text-xs text-slate-600 leading-relaxed">
                  {scheme.description}
                </p>

                {scheme.applicable_sectors && (
                  <div className="space-y-1 pt-2 border-t border-slate-100">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">{t("certification.covered_sectors", "Covered Sectors")}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {scheme.applicable_sectors.map((sec) => (
                        <span key={sec} className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">
                          {sec}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {scheme.fee_structure_summary && (
                  <div className="space-y-1 pt-2 border-t border-slate-100">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">{t("certification.fee_structure", "Fee Structure")}</p>
                    <p className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                      {scheme.fee_structure_summary}
                    </p>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100">
                <button
                  onClick={() => {
                    setActiveTab("wizard");
                    setProductInput(scheme.name);
                    loadRoadmap(scheme.name);
                  }}
                  className="w-full bg-slate-100 hover:bg-bis-navy hover:text-white text-slate-800 font-bold py-2 rounded-xl text-xs transition-colors flex items-center justify-center space-x-1.5"
                >
                  <span>{t("certification.generate_for_scheme", "Generate Roadmap for this Scheme")}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CertificationPage() {
  const { t } = useLanguage();
  return (
    <Suspense fallback={<div className="bg-white p-12 rounded-xl border border-slate-200 text-center text-slate-500 text-sm">{t("certification.loading_roadmap", "Loading Certification Roadmap...")}</div>}>
      <CertificationContent />
    </Suspense>
  );
}
