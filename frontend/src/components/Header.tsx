"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  ShieldCheck,
  Globe,
  Search,
  Menu,
  X,
  ExternalLink,
  BotMessageSquare,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

interface HeaderProps {
  onToggleMobileMenu?: () => void;
  mobileMenuOpen?: boolean;
}

export function Header({ onToggleMobileMenu, mobileMenuOpen }: HeaderProps) {
  const { language, setLanguage, t } = useLanguage();
  const pathname = usePathname();
  const router = useRouter();
  const [quickSearch, setQuickSearch] = useState("");

  const getPageTitle = () => {
    if (pathname === "/") return t("nav.dashboard", "Overview / Dashboard");
    if (pathname.startsWith("/assistant")) return t("nav.assistant", "Ask Sahayak AI Assistant");
    if (pathname.startsWith("/standards")) return t("nav.standards", "Indian Standards Explorer");
    if (pathname.startsWith("/certification")) return t("nav.certification", "Certification Guidance");
    if (pathname.startsWith("/laboratories")) return t("nav.laboratories", "Testing Laboratory Directory");
    if (pathname.startsWith("/about")) return t("nav.about", "About & Architecture");
    if (pathname.startsWith("/admin")) return "Administrative Console";
    return "e-BIS Sahayak Portal";
  };

  const handleQuickSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickSearch.trim()) return;
    router.push(`/assistant?prompt=${encodeURIComponent(quickSearch.trim())}`);
    setQuickSearch("");
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
      {/* Top National Government Identity Ribbon */}
      <div className="gov-tricolor-accent w-full" />
      <div className="bg-[#071324] px-4 sm:px-6 py-1.5 text-xs text-slate-300 flex justify-between items-center border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          <span className="font-bold text-amber-400 tracking-wider uppercase text-[10px]">
            {t("header.national_portal_title", "Government of India")}
          </span>
          <span className="text-slate-600 hidden sm:inline">•</span>
          <span className="text-slate-300 hidden sm:inline text-[11px] font-medium">
            Ministry of Consumer Affairs, Food & Public Distribution
          </span>
          <span className="text-slate-600 hidden md:inline">•</span>
          <span className="text-slate-300 hidden md:inline text-[11px] font-medium">
            Bureau of Indian Standards (BIS)
          </span>
        </div>

        {/* Language Selector Pills */}
        <div className="flex items-center space-x-2">
          <Globe className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <div
            className="inline-flex bg-slate-900 rounded-lg p-0.5 border border-slate-750 text-[11px] font-semibold"
            role="group"
            aria-label="Language Selector"
          >
            <button
              onClick={() => setLanguage("en")}
              aria-pressed={language === "en"}
              className={`px-2.5 py-0.5 rounded-md transition-all ${
                language === "en"
                  ? "bg-amber-500 text-slate-950 font-bold shadow-xs"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage("hi")}
              aria-pressed={language === "hi"}
              className={`px-2.5 py-0.5 rounded-md transition-all ${
                language === "hi"
                  ? "bg-amber-500 text-slate-950 font-bold shadow-xs"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              हिन्दी
            </button>
            <button
              onClick={() => setLanguage("ta")}
              aria-pressed={language === "ta"}
              className={`px-2.5 py-0.5 rounded-md transition-all ${
                language === "ta"
                  ? "bg-amber-500 text-slate-950 font-bold shadow-xs"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              தமிழ்
            </button>
          </div>
        </div>
      </div>

      {/* Main Bar: Current Route Breadcrumb & Search Shortcut */}
      <div className="px-4 sm:px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3 min-w-0">
          {/* Mobile Menu Button */}
          <button
            onClick={onToggleMobileMenu}
            className="md:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors focus-visible:ring-2 focus-visible:ring-amber-500"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          {/* Current Page Title / Breadcrumb */}
          <div className="min-w-0">
            <h1 className="text-base sm:text-lg font-bold text-[#0F172A] truncate">
              {getPageTitle()}
            </h1>
            <p className="text-[11px] text-[#64748B] hidden sm:block truncate">
              Official Indian Standards (IS), QCOs, Schemes & Testing Labs
            </p>
          </div>
        </div>

        {/* Quick Question / Search Input */}
        <div className="flex items-center space-x-3">
          <form
            onSubmit={handleQuickSearchSubmit}
            className="hidden lg:flex items-center relative w-72"
          >
            <input
              type="text"
              value={quickSearch}
              onChange={(e) => setQuickSearch(e.target.value)}
              placeholder={t("header.quick_search", "Ask standard or product...")}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg pl-8 pr-3 py-2 text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-all"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 pointer-events-none" />
          </form>

          {/* Quick Action to Chat */}
          <Link
            href="/assistant"
            className="inline-flex items-center space-x-1.5 bg-[#071324] hover:bg-[#152E4D] text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors shadow-xs"
          >
            <BotMessageSquare className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">{t("header.launch_ai", "Ask Sahayak")}</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
