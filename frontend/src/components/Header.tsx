"use client";

import React from "react";
import Link from "next/link";
import { ShieldCheck, Globe, Sparkles, BotMessageSquare } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export function Header() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <header className="bg-bis-navy text-white border-b border-slate-700 sticky top-0 z-50">
      {/* Top National Identity Bar */}
      <div className="bg-slate-900 px-4 py-1.5 text-xs flex justify-between items-center text-slate-300 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <span className="font-semibold text-bis-saffron">{t("header.national_portal_title", "Government of India")}</span>
          <span className="text-slate-600">|</span>
          <span className="hidden sm:inline text-slate-300">{t("header.bis_title", "Bureau of Indian Standards • e-BIS Sahayak")}</span>
        </div>
        
        {/* Language Selector Buttons */}
        <div className="flex items-center space-x-2">
          <Globe className="w-3.5 h-3.5 text-bis-saffron shrink-0" />
          <div className="inline-flex bg-slate-800 rounded-md p-0.5 border border-slate-700 text-[11px]">
            <button
              onClick={() => setLanguage("en")}
              className={`px-2.5 py-0.5 rounded transition-colors ${
                language === "en" ? "bg-bis-saffron text-slate-950 font-bold shadow-xs" : "text-slate-300 hover:text-white"
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage("hi")}
              className={`px-2.5 py-0.5 rounded transition-colors ${
                language === "hi" ? "bg-bis-saffron text-slate-950 font-bold shadow-xs" : "text-slate-300 hover:text-white"
              }`}
            >
              हिन्दी
            </button>
            <button
              onClick={() => setLanguage("ta")}
              className={`px-2.5 py-0.5 rounded transition-colors ${
                language === "ta" ? "bg-bis-saffron text-slate-950 font-bold shadow-xs" : "text-slate-300 hover:text-white"
              }`}
            >
              தமிழ்
            </button>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-700 to-bis-navy flex items-center justify-center border border-blue-400/30 shadow-md">
              <ShieldCheck className="w-6 h-6 text-bis-saffron" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-xl tracking-tight text-white group-hover:text-blue-200 transition-colors">
                  {t("dashboard.title_main", "e-BIS Sahayak")}
                </span>
              </div>
              <p className="text-xs text-slate-300">
                {t("assistant.subtitle", "Information Assistant for Indian Standards & BIS Services")}
              </p>
            </div>
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          <Link
            href="/assistant"
            className="bg-bis-saffron hover:bg-bis-saffronDark text-slate-900 font-bold px-4 py-2 rounded-xl text-xs sm:text-sm transition-all shadow-sm flex items-center space-x-2"
          >
            <BotMessageSquare className="w-4 h-4 text-slate-900" />
            <span>{t("header.launch_ai", "Ask Sahayak Assistant")}</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
