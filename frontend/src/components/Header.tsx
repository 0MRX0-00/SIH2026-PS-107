"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldCheck,
  Globe,
  Sparkles,
  BotMessageSquare,
  Menu,
  X,
  LayoutDashboard,
  FileSearch,
  Award,
  FlaskConical,
  Info,
  Building2,
  ExternalLink,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export function Header() {
  const { language, setLanguage, t } = useLanguage();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const NAV_ITEMS = [
    { href: "/", label: t("nav.dashboard", "Dashboard"), icon: LayoutDashboard },
    { href: "/assistant", label: t("nav.assistant", "Sahayak Assistant"), icon: BotMessageSquare },
    { href: "/standards", label: t("nav.standards", "Standards Explorer"), icon: FileSearch },
    { href: "/certification", label: t("nav.certification", "Certification Guidance"), icon: Award },
    { href: "/laboratories", label: t("nav.laboratories", "Testing Laboratories"), icon: FlaskConical },
    { href: "/about", label: t("nav.about", "About e-BIS Sahayak"), icon: Info },
  ];

  return (
    <header className="bg-slate-950 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
      {/* Top Government Identity Bar */}
      <div className="bg-slate-900/90 backdrop-blur-xs px-4 py-1 text-xs flex justify-between items-center text-slate-300 border-b border-slate-800/80">
        <div className="flex items-center space-x-2.5">
          <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse shrink-0" />
          <span className="font-semibold text-amber-400 tracking-wide uppercase text-[10px]">
            {t("header.national_portal_title", "Government of India")}
          </span>
          <span className="text-slate-700">|</span>
          <span className="hidden sm:inline text-slate-300 text-[11px] font-medium">
            {t("header.bis_title", "Bureau of Indian Standards • e-BIS Sahayak Portal")}
          </span>
        </div>

        {/* Language Switcher Pills */}
        <div className="flex items-center space-x-2">
          <Globe className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <div className="inline-flex bg-slate-950 rounded-lg p-0.5 border border-slate-800 text-[11px] font-semibold">
            <button
              onClick={() => setLanguage("en")}
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

      {/* Main Header Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>

          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-700 via-blue-900 to-slate-950 flex items-center justify-center border border-amber-400/40 shadow-lg group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-amber-300 transition-colors">
                  {t("dashboard.title_main", "e-BIS Sahayak")}
                </span>
                <span className="bg-amber-500/20 text-amber-300 border border-amber-400/30 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider hidden sm:inline-block">
                  AI Grounded
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                {t("assistant.subtitle", "Information Assistant for Indian Standards & BIS Services")}
              </p>
            </div>
          </Link>
        </div>

        {/* Action Button */}
        <div className="flex items-center space-x-3">
          <Link
            href="/assistant"
            className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs sm:text-sm transition-all shadow-md hover:shadow-amber-500/20 flex items-center space-x-2 group"
          >
            <BotMessageSquare className="w-4 h-4 text-slate-950 group-hover:rotate-6 transition-transform" />
            <span className="hidden sm:inline">{t("header.launch_ai", "Ask Sahayak Assistant")}</span>
            <span className="sm:hidden">Ask AI</span>
          </Link>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-800 bg-slate-900/95 backdrop-blur-md px-4 py-4 space-y-3">
          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-amber-400" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}
