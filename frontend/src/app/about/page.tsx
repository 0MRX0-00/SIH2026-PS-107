"use client";

import React from "react";
import Link from "next/link";
import {
  ShieldCheck,
  BotMessageSquare,
  FileSearch,
  Award,
  FlaskConical,
  Globe,
  CheckCircle2,
  Lock,
  ArrowRight,
  Sparkles,
  HelpCircle,
  Building2,
  Layers,
  FileText
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function AboutPage() {
  const { t, language } = useLanguage();

  return (
    <div className="space-y-10 pb-16 max-w-5xl mx-auto">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-bis-navy via-slate-900 to-blue-950 rounded-2xl p-8 sm:p-12 text-white shadow-xl border border-slate-700 relative overflow-hidden">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center space-x-2 bg-blue-500/20 text-blue-300 border border-blue-400/30 px-3.5 py-1 rounded-full text-xs font-bold tracking-wide">
            <Sparkles className="w-3.5 h-3.5 text-bis-saffron" />
            <span>{t("about.hero_badge", "About e-BIS Sahayak")}</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            {t("about.hero_title", "Intelligent Guidance for Indian Standards & BIS Services")}
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            {t(
              "about.hero_desc",
              "e-BIS Sahayak is an intelligent information assistant designed to help manufacturers, businesses, consumers, and researchers navigate Indian Standards (IS), conformity assessment schemes, and testing laboratory networks with confidence."
            )}
          </p>
        </div>
      </div>

      {/* Core Objectives / What It Does */}
      <div className="space-y-4">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-slate-900">
            {t("about.what_title", "What e-BIS Sahayak Does")}
          </h2>
          <p className="text-xs text-slate-500">
            {t("about.what_subtitle", "Bridging the gap between technical standard publications and real-world compliance.")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-bis-blue">
              <FileSearch className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-sm">
              {t("about.feature_1_title", "Standards & Clause Exploration")}
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t(
                "about.feature_1_desc",
                "Instant search and clause-by-clause inspection across electrotechnical, electronics, IT, food, civil, and mechanical standards with mandatory QCO notifications."
              )}
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600">
              <Award className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-sm">
              {t("about.feature_2_title", "Certification Roadmaps")}
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t(
                "about.feature_2_desc",
                "Step-by-step guidance for Scheme-I (ISI Mark), Scheme-II (Compulsory Registration Scheme - CRS), and FMCS for foreign manufacturers with document checklists and fee structures."
              )}
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600">
              <FlaskConical className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-900 text-sm">
              {t("about.feature_3_title", "Testing Laboratories Directory")}
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t(
                "about.feature_3_desc",
                "Discover recognized testing facilities across India categorized by state, accreditation scope, and specific Indian Standard testing capabilities."
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Who It Helps */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-slate-900">
            {t("about.who_title", "Who We Help")}
          </h2>
          <p className="text-xs text-slate-500">
            {t("about.who_subtitle", "Built for diverse stakeholders in the Indian quality ecosystem.")}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 space-y-2">
            <span className="text-xs font-bold text-bis-blue uppercase">
              {t("about.who_1_title", "01. Manufacturers & MSMEs")}
            </span>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t("about.who_1_desc", "Identify mandatory Quality Control Orders (QCOs), testing parameters, and compliance pathways for domestic production.")}
            </p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 space-y-2">
            <span className="text-xs font-bold text-bis-blue uppercase">
              {t("about.who_2_title", "02. Startups & Importers")}
            </span>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t("about.who_2_desc", "Navigate CRS registration requirements for electronic goods and FMCS requirements for foreign manufacturing facilities.")}
            </p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 space-y-2">
            <span className="text-xs font-bold text-bis-blue uppercase">
              {t("about.who_3_title", "03. Consumers & Buyers")}
            </span>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t("about.who_3_desc", "Understand standard safety marks, verify product authenticity, and learn about national safety specifications.")}
            </p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 space-y-2">
            <span className="text-xs font-bold text-bis-blue uppercase">
              {t("about.who_4_title", "04. Quality Auditors & Labs")}
            </span>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t("about.who_4_desc", "Inspect test clauses, environmental ratings, and testing scopes across recognized national facilities.")}
            </p>
          </div>
        </div>
      </div>

      {/* Evidence-First & Trust Guarantee */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-700">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              {t("about.trust_title", "Evidence-First Information & Transparency")}
            </h2>
            <p className="text-xs text-slate-500">
              {t("about.trust_subtitle", "How we ensure verifiable answers without speculation.")}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-600 leading-relaxed">
          <div className="space-y-1.5 p-4 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5 font-bold text-slate-800">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{t("about.pillar_1_title", "Grounded Citations")}</span>
            </div>
            <p>
              {t("about.pillar_1_desc", "Every response is bounded by verified BIS source documents. Users can click citation pills to inspect verbatim clauses, section numbers, and page numbers.")}
            </p>
          </div>
          <div className="space-y-1.5 p-4 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5 font-bold text-slate-800">
              <Lock className="w-4 h-4 text-emerald-600" />
              <span>{t("about.pillar_2_title", "Strict Evidence Boundary")}</span>
            </div>
            <p>
              {t("about.pillar_2_desc", "If a query lacks authoritative evidence in the indexed knowledge base, the assistant explicitly states the limitation rather than fabricating ungrounded specifications.")}
            </p>
          </div>
          <div className="space-y-1.5 p-4 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center space-x-1.5 font-bold text-slate-800">
              <Globe className="w-4 h-4 text-emerald-600" />
              <span>{t("about.pillar_3_title", "Multilingual Accessibility")}</span>
            </div>
            <p>
              {t("about.pillar_3_desc", "Full native support for English, हिन्दी (Hindi), and தமிழ் (Tamil) across the user interface, standards catalogue, and conversational assistant.")}
            </p>
          </div>
        </div>
      </div>

      {/* Official Advisory & Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-xs text-amber-900 space-y-2">
        <div className="flex items-center space-x-2 font-bold text-amber-950">
          <HelpCircle className="w-4 h-4 text-amber-700 shrink-0" />
          <span>{t("about.disclaimer_title", "Important Advisory & Information Notice")}</span>
        </div>
        <p className="leading-relaxed text-amber-800">
          {t(
            "about.disclaimer_body",
            "e-BIS Sahayak is an informational assistant developed to assist stakeholders in understanding Indian Standards and BIS conformity pathways. While all information is grounded in official BIS publications, this application does not constitute legal certification, statutory authorization, or formal approval. Manufacturers and applicants must complete their formal licensing, application submissions, and fee payments through the official e-BIS / ManakOnline portal (manakonline.in)."
          )}
        </p>
      </div>

      {/* Quick Action Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200">
        <Link
          href="/assistant"
          className="bg-bis-blue hover:bg-blue-900 text-white font-bold px-6 py-3 rounded-xl text-xs sm:text-sm flex items-center space-x-2 transition-all shadow-sm"
        >
          <BotMessageSquare className="w-4 h-4" />
          <span>{t("about.cta_assistant", "Ask e-BIS Sahayak")}</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
        <Link
          href="/standards"
          className="bg-white hover:bg-slate-50 text-slate-800 font-bold px-6 py-3 rounded-xl text-xs sm:text-sm border border-slate-300 flex items-center space-x-2 transition-all"
        >
          <FileSearch className="w-4 h-4 text-bis-blue" />
          <span>{t("about.cta_standards", "Explore Indian Standards")}</span>
        </Link>
        <Link
          href="/certification"
          className="bg-white hover:bg-slate-50 text-slate-800 font-bold px-6 py-3 rounded-xl text-xs sm:text-sm border border-slate-300 flex items-center space-x-2 transition-all"
        >
          <Award className="w-4 h-4 text-amber-600" />
          <span>{t("about.cta_certification", "Certification Schemes")}</span>
        </Link>
      </div>
    </div>
  );
}
