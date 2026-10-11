"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ShieldCheck,
  BotMessageSquare,
  FileSearch,
  Award,
  FlaskConical,
  Sparkles,
  ArrowRight,
  Search,
  Mic,
  MicOff,
  Clock,
  ExternalLink,
  CheckCircle2,
  BookOpen,
  Building,
  HelpCircle,
  FileText,
  Layers,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import {
  getRecentConsultations,
  saveRecentConsultation,
  RecentConsultation,
} from "@/lib/consultations";

export default function DashboardPage() {
  const router = useRouter();
  const { t, language } = useLanguage();
  const [queryInput, setQueryInput] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [recentConsultations, setRecentConsultations] = useState<RecentConsultation[]>([]);
  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition if supported in browser
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        setSpeechSupported(true);
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang =
          language === "hi" ? "hi-IN" : language === "ta" ? "ta-IN" : "en-IN";

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setQueryInput(transcript);
          setIsListening(false);
        };

        recognition.onerror = () => {
          setIsListening(false);
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
      }
    }
  }, [language]);

  // Load recent consultations
  useEffect(() => {
    const loadConsultations = () => {
      setRecentConsultations(getRecentConsultations());
    };
    loadConsultations();
    window.addEventListener("ebis_consultations_updated", loadConsultations);
    return () => {
      window.removeEventListener("ebis_consultations_updated", loadConsultations);
    };
  }, []);

  const handleVoiceToggle = () => {
    if (!speechSupported || !recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.lang =
          language === "hi" ? "hi-IN" : language === "ta" ? "ta-IN" : "en-IN";
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.warn("Speech recognition start failed", err);
        setIsListening(false);
      }
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput.trim()) return;
    const q = queryInput.trim();
    saveRecentConsultation(q);
    router.push(`/assistant?prompt=${encodeURIComponent(q)}`);
  };

  const handleSampleClick = (sampleQuery: string) => {
    setQueryInput(sampleQuery);
    saveRecentConsultation(sampleQuery);
    router.push(`/assistant?prompt=${encodeURIComponent(sampleQuery)}`);
  };

  const sampleQueries = {
    en: [
      {
        tag: "Standard Scope",
        query: "What is IS 1293:2019 and what are its safety requirements for plugs and sockets?",
      },
      {
        tag: "Product Discovery",
        query: "Which Indian Standard and mandatory QCO applies to stainless steel water bottles?",
      },
      {
        tag: "Certification Wizard",
        query: "What is the procedure and document checklist for Scheme-II CRS for mobile phone chargers?",
      },
      {
        tag: "Testing Facility",
        query: "Where can I test ceiling fans under IS 17803 in Maharashtra or Gujarat?",
      },
    ],
    hi: [
      {
        tag: "मानक दायरा",
        query: "IS 1293:2019 क्या है और प्लग और सॉकेट के लिए सुरक्षा आवश्यकताएं क्या हैं?",
      },
      {
        tag: "उत्पाद खोज",
        query: "स्टेनलेस स्टील पानी की बोतलों पर कौन सा भारतीय मानक और अनिवार्य QCO लागू होता है?",
      },
      {
        tag: "प्रमाणन प्रक्रिया",
        query: "मोबाइल फोन चार्जर के लिए योजना-II CRS की प्रक्रिया और आवश्यक दस्तावेज क्या हैं?",
      },
      {
        tag: "परीक्षण प्रयोगशाला",
        query: "महाराष्ट्र या गुजरात में IS 17803 के तहत सीलिंग पंखे का परीक्षण कहाँ करवा सकते हैं?",
      },
    ],
    ta: [
      {
        tag: "தரநிலை நோக்கம்",
        query: "IS 1293:2019 என்றால் என்ன மற்றும் பிளக் மற்றும் சாக்கெட்டுகளுக்கான பாதுகாப்பு தேவைகள் என்ன?",
      },
      {
        tag: "தயாரிப்பு கண்டறிதல்",
        query: "துருப்பிடிக்காத எஃகு தண்ணீர் பாட்டில்களுக்கு எந்த இந்திய தரநிலை மற்றும் கட்டாய QCO பொருந்தும்?",
      },
      {
        tag: "சான்றிதழ் வழிகாட்டி",
        query: "மொபைல் போன் சார்ஜர்களுக்கான திட்டம்-II CRS நடைமுறை மற்றும் ஆவணப் பட்டியல் என்ன?",
      },
      {
        tag: "சோதனை ஆய்வகம்",
        query: "தமிழ்நாட்டில் IS 17803 இன் கீழ் மின் விசிறிகளை சோதிக்கக்கூடிய ஆய்வகங்கள் எங்கே உள்ளன?",
      },
    ],
  };

  const currentSampleQueries = sampleQueries[language] || sampleQueries.en;

  const FEATURE_CARDS = [
    {
      title: t("dashboard.card_assistant_title", "Ask Sahayak AI"),
      desc: t(
        "dashboard.card_assistant_desc",
        "Source-grounded regulatory guidance powered by Groq LPU inference. Resolves standard requirements, QCOs, and clauses."
      ),
      href: "/assistant",
      icon: BotMessageSquare,
      badge: "Fast Inference",
      badgeColor: "bg-blue-100 text-blue-800",
      cta: t("dashboard.card_assistant_cta", "Start Consultation"),
    },
    {
      title: t("dashboard.card_standards_title", "Explore Indian Standards"),
      desc: t(
        "dashboard.card_standards_desc",
        "Search authentic Indian Standards (IS), mandatory Quality Control Orders, technical committees, and technical clauses."
      ),
      href: "/standards",
      icon: FileSearch,
      badge: "Verified Catalogue",
      badgeColor: "bg-amber-100 text-amber-800",
      cta: t("dashboard.card_standards_cta", "Search Standards"),
    },
    {
      title: t("dashboard.card_cert_title", "Certification Guidance"),
      desc: t(
        "dashboard.card_cert_desc",
        "Interactive 4-step roadmap for Scheme-I (ISI Mark), Scheme-II (CRS), and Scheme-IV (FMCS) with document checklists."
      ),
      href: "/certification",
      icon: Award,
      badge: "Roadmap Wizard",
      badgeColor: "bg-purple-100 text-purple-800",
      cta: t("dashboard.card_cert_cta", "View Schemes"),
    },
    {
      title: t("dashboard.card_lab_title", "Find a Testing Laboratory"),
      desc: t(
        "dashboard.card_lab_desc",
        "Locate 576 accredited laboratory facilities across 27 States and Union Territories with direct BIS LIMS directory links."
      ),
      href: "/laboratories",
      icon: FlaskConical,
      badge: "576 Labs",
      badgeColor: "bg-emerald-100 text-emerald-800",
      cta: t("dashboard.card_lab_cta", "Find Laboratories"),
    },
  ];

  const OFFICIAL_PORTALS = [
    {
      name: t("dashboard.portal_bis_name", "Bureau of Indian Standards"),
      url: "https://www.bis.gov.in",
      desc: t(
        "dashboard.portal_bis_desc",
        "National Standards Body of India portal with official gazette orders and notifications."
      ),
    },
    {
      name: t("dashboard.portal_manak_name", "Manakonline e-Portal"),
      url: "https://www.manakonline.in",
      desc: t(
        "dashboard.portal_manak_desc",
        "Digital e-BIS portal for product certification, laboratory recognition, and hallmarking."
      ),
    },
    {
      name: t("dashboard.portal_lims_name", "BIS LIMS Laboratory Portal"),
      url: "https://lims.bis.gov.in",
      desc: t(
        "dashboard.portal_lims_desc",
        "Laboratory Information Management System for test requests and accreditation data."
      ),
    },
    {
      name: t("dashboard.portal_care_name", "BIS Care Mobile App"),
      url: "https://www.bis.gov.in/index.php/bis-care-app/",
      desc: t(
        "dashboard.portal_care_desc",
        "Consumer app for verifying ISI marks, Hallmark authenticity, and lodging complaints."
      ),
    },
  ];

  return (
    <div className="space-y-8 pb-10">
      {/* 1. Welcome Section */}
      <div className="bg-gradient-to-br from-[#071324] via-[#0d213a] to-[#152E4D] rounded-3xl p-6 sm:p-10 text-white shadow-xl border border-slate-800 relative overflow-hidden">
        {/* Subtle decorative emblem */}
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none hidden lg:block">
          <ShieldCheck className="w-80 h-80 text-amber-400" />
        </div>
        <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-3xl relative z-10 space-y-4">
          <div className="inline-flex items-center space-x-2 bg-amber-500/15 text-amber-300 border border-amber-400/30 px-3.5 py-1 rounded-full text-xs font-bold tracking-wide backdrop-blur-xs">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>SIH 2026 Problem Statement #107 • Bureau of Indian Standards</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
            {t("dashboard.welcome_title", "Welcome to e-BIS Sahayak")}
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
            {t(
              "dashboard.welcome_subtitle",
              "Your intelligent assistant for understanding Indian Standards (IS), mandatory Quality Control Orders (QCOs), certification schemes (ISI Mark, CRS, FMCS), and accredited testing laboratories in English, हिन्दी, and தமிழ்."
            )}
          </p>

          {/* 2. Main AI Query Area */}
          <div className="pt-2">
            <form onSubmit={handleSearchSubmit} className="relative flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  placeholder={t(
                    "dashboard.search_placeholder",
                    "Ask Sahayak in English, हिन्दी, or தமிழ் (e.g., 'What is IS 1293?')..."
                  )}
                  className="w-full text-sm bg-white/95 text-slate-900 placeholder-slate-400 pl-11 pr-12 py-3.5 rounded-2xl border border-slate-200 shadow-md focus:bg-white focus:outline-hidden focus:ring-3 focus:ring-amber-500 focus:border-amber-500 transition-all"
                  aria-label="Ask Sahayak AI Query Input"
                />
                <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />

                {/* Voice Input Button */}
                {speechSupported && (
                  <button
                    type="button"
                    onClick={handleVoiceToggle}
                    className={`absolute right-3.5 top-1/2 -translate-y-1/2 p-1.5 rounded-xl transition-all ${
                      isListening
                        ? "bg-rose-500 text-white animate-pulse"
                        : "text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                    }`}
                    title={isListening ? "Listening... Click to stop" : "Speak your query"}
                    aria-label="Voice input button"
                  >
                    {isListening ? <Mic className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </button>
                )}
              </div>

              <button
                type="submit"
                className="bg-amber-500 hover:bg-amber-400 active:scale-[0.98] text-slate-950 font-bold px-6 py-3.5 rounded-2xl shadow-lg transition-all flex items-center justify-center space-x-2 shrink-0 focus-visible:ring-2 focus-visible:ring-amber-300"
              >
                <span>{t("dashboard.ask_ai_btn", "Ask Sahayak AI")}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            {/* Example Queries Chips */}
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <p className="text-[11px] font-semibold text-slate-400 mb-2">
                {t("dashboard.try_asking", "Suggested queries:")}
              </p>
              <div className="flex flex-wrap gap-2">
                {currentSampleQueries.map((sample, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSampleClick(sample.query)}
                    className="inline-flex items-center space-x-1.5 bg-slate-900/80 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-750 hover:border-amber-500/50 px-3 py-1.5 rounded-xl text-xs transition-all text-left group"
                  >
                    <span className="text-[10px] font-bold text-amber-400 uppercase">
                      {sample.tag}:
                    </span>
                    <span className="truncate max-w-xs">{sample.query}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Core Feature Cards (2x2 Grid) */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-[#0F172A]">
              {t("dashboard.core_features_title", "e-BIS Sahayak Core Modules")}
            </h2>
            <p className="text-xs text-[#64748B]">
              Direct access to standards navigation, certification schemes, and testing facilities
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURE_CARDS.map((card, idx) => {
            const Icon = card.icon;
            return (
              <Link
                key={idx}
                href={card.href}
                className="bg-white border border-slate-200 hover:border-amber-500/40 rounded-2xl p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-800 group-hover:bg-[#071324] group-hover:text-amber-400 transition-colors">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${card.badgeColor}`}
                    >
                      {card.badge}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-sm text-[#0F172A] group-hover:text-blue-900 transition-colors">
                      {card.title}
                    </h3>
                    <p className="text-xs text-[#64748B] mt-1 line-clamp-3 leading-relaxed">
                      {card.desc}
                    </p>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-amber-600 group-hover:text-amber-500">
                  <span>{card.cta}</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* 4. Recent Consultations & Official Resources (2 Columns) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent Consultations */}
        <div className="lg:col-span-1 bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-amber-600" />
              <h3 className="text-sm font-bold text-[#0F172A]">
                {t("dashboard.recent_title", "Recent Consultations")}
              </h3>
            </div>
            {recentConsultations.length > 0 && (
              <span className="text-[10px] font-bold bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-full">
                {recentConsultations.length}
              </span>
            )}
          </div>

          <div className="mt-3 flex-1 flex flex-col justify-between">
            {recentConsultations.length === 0 ? (
              <div className="text-center py-8 px-4 text-slate-400 space-y-2">
                <BotMessageSquare className="w-8 h-8 mx-auto text-slate-300" />
                <p className="text-xs font-medium text-slate-600">
                  {t("dashboard.no_recent", "No recent consultations yet")}
                </p>
                <p className="text-[11px] text-slate-400">
                  Your recent queries will appear here for fast follow-up.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {recentConsultations.slice(0, 4).map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleSampleClick(item.query)}
                    className="w-full text-left p-2.5 rounded-xl border border-slate-100 hover:border-amber-400/50 hover:bg-slate-50 transition-all group"
                  >
                    <p className="text-xs font-semibold text-slate-800 group-hover:text-blue-900 truncate">
                      {item.query}
                    </p>
                    <span className="text-[10px] text-slate-400">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </span>
                  </button>
                ))}
              </div>
            )}

            <Link
              href="/assistant"
              className="mt-4 block text-center text-xs font-bold text-[#071324] hover:text-amber-600 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors"
            >
              {t("dashboard.open_assistant_btn", "Open Full AI Assistant →")}
            </Link>
          </div>
        </div>

        {/* Right Column: Official Portals & Verified Governance */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
          <div className="pb-3 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <h3 className="text-sm font-bold text-[#0F172A]">
                {t("dashboard.portals_title", "Official Government Portals & Statutory Verification")}
              </h3>
            </div>
            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
              {t("dashboard.authoritative_bis", "Authoritative BIS")}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
            {OFFICIAL_PORTALS.map((portal, idx) => (
              <a
                key={idx}
                href={portal.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 group-hover:text-blue-900">
                      {portal.name}
                    </span>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 shrink-0" />
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1.5 leading-relaxed">
                    {portal.desc}
                  </p>
                </div>
                <div className="mt-3 flex items-center space-x-1 text-[10px] text-emerald-600 font-semibold">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>{t("dashboard.whitelisted_domain", "Whitelisted Government Domain")}</span>
                </div>
              </a>
            ))}
          </div>

          {/* Architecture Trust Note */}
          <div className="mt-4 p-3.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600 flex items-start space-x-2.5">
            <CheckCircle2 className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
            <div className="text-[11px] leading-relaxed">
              <strong className="text-slate-800">
                {t("dashboard.grounded_architecture_title", "Grounded Provenance Architecture:")}
              </strong>{" "}
              {t(
                "dashboard.grounded_architecture_text",
                "e-BIS Sahayak responses are synthesized using Groq LPU fast inference with strict evidence constraints from the authentic Bureau of Indian Standards catalogue. Unindexed standards receive transparent abstention notices."
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
