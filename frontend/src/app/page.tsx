"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ShieldCheck,
  BotMessageSquare,
  FileSearch,
  Award,
  FlaskConical,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Search,
  Compass,
  Building2,
  FileText,
  HelpCircle,
  Globe,
  Lock,
  Layers
} from "lucide-react";
import { listStandards, listLaboratories, listCertificationSchemes } from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

export default function DashboardPage() {
  const router = useRouter();
  const { t, language } = useLanguage();
  const [queryInput, setQueryInput] = useState("");
  const [stats, setStats] = useState({
    standardsCount: 4,
    labsCount: 5,
    schemesCount: 3,
  });

  useEffect(() => {
    Promise.all([
      listStandards().catch(() => []),
      listLaboratories().catch(() => []),
      listCertificationSchemes().catch(() => []),
    ]).then(([stds, labs, schemes]) => {
      setStats({
        standardsCount: stds.length || 4,
        labsCount: labs.length || 5,
        schemesCount: schemes.length || 3,
      });
    });
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput.trim()) return;
    router.push(`/assistant?prompt=${encodeURIComponent(queryInput.trim())}`);
  };

  const sampleQueries = {
    en: [
      { label: "IS 1293 Plugs & Sockets", query: "What are the temperature rise requirements in IS 1293:2019 Clause 19.1?" },
      { label: "Product Discovery", query: "I manufacture stainless steel water bottles. Which Indian standard applies?" },
      { label: "CRS Registration", query: "What is the procedure for Scheme-II Compulsory Registration for power adapters?" },
      { label: "Find Testing Lab", query: "Where can I test electrical appliances in Tamil Nadu?" },
    ],
    hi: [
      { label: "IS 1293 प्लग और सॉकेट", query: "IS 1293:2019 खंड 19.1 में तापमान वृद्धि की आवश्यकताएं क्या हैं?" },
      { label: "उत्पाद खोज", query: "मैं स्टेनलेस स्टील पानी की बोतल बनाता हूँ। कौन सा भारतीय मानक लागू होता है?" },
      { label: "CRS पंजीकरण", query: "पावर एडाप्टर के लिए योजना-II अनिवार्य पंजीकरण प्रक्रिया क्या है?" },
      { label: "परीक्षण प्रयोगशाला", query: "उत्तर प्रदेश में विद्युत उपकरणों के परीक्षण के लिए कौन सी प्रयोगशाला है?" },
    ],
    ta: [
      { label: "IS 1293 பிளக் & சாக்கெட்", query: "IS 1293:2019 பிரிவு 19.1 இன் கீழ் வெப்பநிலை அதிகரிப்பு தேவைகள் என்ன?" },
      { label: "தயாரிப்பு தரநிலை", query: "நான் துருப்பிடிக்காத எஃகு தண்ணீர் பாட்டில்களை தயாரிக்கிறேன். எந்த இந்திய தரநிலை பொருந்தும்?" },
      { label: "CRS பதிவு", query: "பவர் அடாப்டர்களுக்கான திட்டம்-II கட்டாய பதிவு நடைமுறை என்ன?" },
      { label: "ஆய்வகம் கண்டறிதல்", query: "தமிழ்நாட்டில் மின் சாதனங்களை சோதிக்கக்கூடிய ஆய்வகங்கள் எங்கே உள்ளன?" },
    ]
  };

  const activeQueries = sampleQueries[language] || sampleQueries.en;

  return (
    <div className="space-y-8 pb-12">
      {/* Banner / Hero Section */}
      <div className="bg-gradient-to-r from-bis-navy via-slate-900 to-blue-950 rounded-2xl p-6 sm:p-10 text-white shadow-xl border border-slate-700 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none hidden lg:block">
          <ShieldCheck className="w-80 h-80 text-white" />
        </div>
        
        <div className="max-w-3xl relative z-10 space-y-5">
          <div className="inline-flex items-center space-x-2 bg-blue-500/20 text-blue-300 border border-blue-400/30 px-3.5 py-1 rounded-full text-xs font-bold tracking-wide">
            <Sparkles className="w-3.5 h-3.5 text-bis-saffron" />
            <span>{t("dashboard.badge", "Intelligent Information & Guidance for Indian Standards")}</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            {t("dashboard.title_main", "e-BIS Sahayak")} —{" "}
            <span className="text-bis-saffron font-bold">{t("dashboard.title_highlight", "Understand Indian Standards. Navigate BIS services with confidence.")}</span>
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
            {t("dashboard.description", "Find relevant standards, understand certification requirements, explore laboratory information, and get evidence-backed answers from authoritative BIS documentation.")}
          </p>

          {/* Quick Query Input Bar */}
          <form onSubmit={handleSearchSubmit} className="pt-2">
            <div className="relative flex items-center max-w-2xl bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-1.5 focus-within:border-bis-saffron focus-within:ring-2 focus-within:ring-bis-saffron/20 transition-all">
              <Search className="w-5 h-5 text-slate-300 ml-3 shrink-0" />
              <input
                type="text"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                placeholder={t("dashboard.search_placeholder", "Ask Sahayak in English, हिन्दी, or தமிழ்...")}
                className="w-full bg-transparent border-none text-white placeholder-slate-400 text-sm px-3 py-2 focus:outline-none"
              />
              <button
                type="submit"
                className="bg-bis-saffron hover:bg-bis-saffronDark text-slate-950 font-bold px-4 py-2 rounded-lg text-sm transition-all shadow shrink-0 flex items-center space-x-1"
              >
                <span>{t("dashboard.ask_ai_btn", "Ask Sahayak")}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Sample Query Chips */}
          <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
            <span className="text-slate-400 font-medium">{t("dashboard.try_asking", "Suggested questions:")}</span>
            {activeQueries.map((item, idx) => (
              <button
                key={idx}
                onClick={() => router.push(`/assistant?prompt=${encodeURIComponent(item.query)}`)}
                className="bg-white/5 hover:bg-white/15 text-slate-300 border border-white/10 px-2.5 py-1 rounded-full transition-all text-left"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Core Action Cards (4 Pillars of BIS Services) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
            <Compass className="w-5 h-5 text-bis-blue" />
            <span>{t("dashboard.core_modules", "What You Can Do")}</span>
          </h2>
          <span className="text-xs font-semibold text-slate-500">{t("dashboard.grounded_subtitle", "Evidence-Backed Information")}</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Ask Assistant */}
          <Link
            href="/assistant"
            className="group bg-white rounded-xl border border-slate-200 hover:border-bis-blue p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-blue-50 text-bis-blue flex items-center justify-center group-hover:scale-105 transition-transform">
                <BotMessageSquare className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-slate-900 text-base group-hover:text-bis-blue transition-colors">
                {t("dashboard.assistant_card_title", "Ask the Assistant")}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {t("dashboard.assistant_card_desc", "Get answers about Indian Standards, BIS services, certification and testing.")}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-bis-blue space-x-1 group-hover:translate-x-1 transition-transform">
              <span>{t("dashboard.assistant_card_btn", "Ask Sahayak")}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          {/* Card 2: Find a Standard */}
          <Link
            href="/standards"
            className="group bg-white rounded-xl border border-slate-200 hover:border-bis-blue p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                <FileSearch className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-slate-900 text-base group-hover:text-emerald-700 transition-colors">
                {t("dashboard.standards_card_title", "Find a Standard")}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {t("dashboard.standards_card_desc", "Discover standards relevant to your product, material, or industry.")}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-emerald-600 space-x-1 group-hover:translate-x-1 transition-transform">
              <span>{t("dashboard.standards_card_btn", "Explore Standards")}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          {/* Card 3: Certification Guidance */}
          <Link
            href="/certification"
            className="group bg-white rounded-xl border border-slate-200 hover:border-bis-blue p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Award className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-slate-900 text-base group-hover:text-amber-700 transition-colors">
                {t("dashboard.cert_card_title", "Certification Guidance")}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {t("dashboard.cert_card_desc", "Understand the certification journey, requirements, checklists, and next steps.")}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-amber-600 space-x-1 group-hover:translate-x-1 transition-transform">
              <span>{t("dashboard.cert_card_btn", "View Guidance")}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          {/* Card 4: Find a Laboratory */}
          <Link
            href="/laboratories"
            className="group bg-white rounded-xl border border-slate-200 hover:border-bis-blue p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                <FlaskConical className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-slate-900 text-base group-hover:text-purple-700 transition-colors">
                {t("dashboard.lab_card_title", "Find a Laboratory")}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {t("dashboard.lab_card_desc", "Explore laboratories and testing information relevant to your product testing needs.")}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-purple-600 space-x-1 group-hover:translate-x-1 transition-transform">
              <span>{t("dashboard.lab_card_btn", "Search Laboratories")}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>
        </div>
      </div>

      {/* How It Works & Transparency Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Knowledge Stats */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2">
            <Building2 className="w-5 h-5 text-bis-blue" />
            <h2 className="text-base font-bold text-slate-900">
              {t("dashboard.verified_repo", "Verified Knowledge Base & Registries")}
            </h2>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
              <p className="text-2xl font-extrabold text-bis-navy">{stats.standardsCount}</p>
              <p className="text-xs font-medium text-slate-500 mt-1">{t("dashboard.verified_standards", "Verified Standards")}</p>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
              <p className="text-2xl font-extrabold text-bis-navy">{stats.schemesCount}</p>
              <p className="text-xs font-medium text-slate-500 mt-1">{t("dashboard.cert_schemes", "Certification Schemes")}</p>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
              <p className="text-2xl font-extrabold text-bis-navy">{stats.labsCount}</p>
              <p className="text-xs font-medium text-slate-500 mt-1">{t("dashboard.accredited_labs", "Testing Facilities")}</p>
            </div>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 text-xs text-emerald-900 flex items-start space-x-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              {t("dashboard.zero_hallucination_note", "Evidence-First Information: Standard requirements, quality control orders, and testing scopes are strictly verified against official BIS source records.")}
            </p>
          </div>
        </div>

        {/* How It Works Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-bis-blue" />
              <h2 className="text-base font-bold text-slate-900">
                {t("dashboard.how_it_works_title", "How It Works")}
              </h2>
            </div>
            <ul className="space-y-2.5 text-xs text-slate-600">
              <li className="flex items-start space-x-2">
                <span className="w-5 h-5 rounded-full bg-blue-50 text-bis-blue font-bold flex items-center justify-center shrink-0 text-[11px]">1</span>
                <span>{t("dashboard.how_step_1", "Ask questions or search for your product in English, Hindi, or Tamil.")}</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="w-5 h-5 rounded-full bg-blue-50 text-bis-blue font-bold flex items-center justify-center shrink-0 text-[11px]">2</span>
                <span>{t("dashboard.how_step_2", "Review verified answers with clickable citations pointing to exact clauses.")}</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="w-5 h-5 rounded-full bg-blue-50 text-bis-blue font-bold flex items-center justify-center shrink-0 text-[11px]">3</span>
                <span>{t("dashboard.how_step_3", "Explore certification pathways and find recognized laboratories across India.")}</span>
              </li>
            </ul>
          </div>

          <Link
            href="/about"
            className="pt-3 border-t border-slate-100 text-xs font-bold text-bis-blue hover:text-blue-900 flex items-center justify-between group"
          >
            <span>{t("dashboard.learn_more", "Learn more about e-BIS Sahayak")}</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>
      </div>
    </div>
  );
}
