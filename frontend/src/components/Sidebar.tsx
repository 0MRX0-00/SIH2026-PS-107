"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  BotMessageSquare,
  FileSearch,
  Award,
  FlaskConical,
  Info,
  Globe,
  ShieldCheck,
  Plus,
  MessageSquare,
  Trash2,
  ExternalLink,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import {
  getRecentConsultations,
  clearRecentConsultations,
  RecentConsultation,
} from "@/lib/consultations";

interface SidebarProps {
  onCloseMobile?: () => void;
}

export function Sidebar({ onCloseMobile }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { t, language } = useLanguage();
  const [recentConsultations, setRecentConsultations] = useState<RecentConsultation[]>([]);

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

  const handleNewConsultation = () => {
    if (onCloseMobile) onCloseMobile();
    router.push("/assistant?new=true");
  };

  const handleRecentClick = (query: string) => {
    if (onCloseMobile) onCloseMobile();
    router.push(`/assistant?prompt=${encodeURIComponent(query)}`);
  };

  const handleClearHistory = (e: React.MouseEvent) => {
    e.stopPropagation();
    clearRecentConsultations();
  };

  const NAV_ITEMS = [
    {
      href: "/",
      label: t("nav.dashboard", "Overview / Dashboard"),
      icon: LayoutDashboard,
      badge: null,
    },
    {
      href: "/assistant",
      label: t("nav.assistant", "Ask Sahayak AI"),
      icon: BotMessageSquare,
      badge: "LPU",
    },
    {
      href: "/standards",
      label: t("nav.standards", "Indian Standards Explorer"),
      icon: FileSearch,
      badge: null,
    },
    {
      href: "/certification",
      label: t("nav.certification", "Certification Guidance"),
      icon: Award,
      badge: "Wizard",
    },
    {
      href: "/laboratories",
      label: t("nav.laboratories", "Laboratory Directory"),
      icon: FlaskConical,
      badge: null,
    },
  ];

  return (
    <aside className="w-64 sm:w-72 bg-[#071324] text-slate-200 border-r border-slate-800 flex flex-col h-full shrink-0 select-none">
      {/* Branding Header */}
      <div className="p-5 border-b border-slate-800/80">
        <Link
          href="/"
          onClick={onCloseMobile}
          className="flex items-center space-x-3 group focus:outline-hidden"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center text-slate-950 shadow-md group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-extrabold text-white text-base tracking-tight">
                e-BIS Sahayak
              </span>
              <span className="text-[10px] font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30 px-1 py-0.2 rounded-xs">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              Bureau of Indian Standards
            </p>
          </div>
        </Link>

        {/* Primary CTA: New Consultation */}
        <button
          onClick={handleNewConsultation}
          className="mt-4 w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs py-2.5 px-4 rounded-xl shadow-md transition-all active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-amber-400"
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          <span>{t("nav.new_consultation", "New Consultation")}</span>
        </button>
      </div>

      {/* Main Scrollable Nav Area */}
      <div className="flex-1 overflow-y-auto px-3.5 py-4 space-y-6">
        {/* Core Navigation Links */}
        <div>
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            {t("nav.services_title", "Main Navigation")}
          </p>
          <nav className="mt-2 space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onCloseMobile}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-[#152E4D] text-white border-l-4 border-amber-500 font-bold shadow-xs"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                  }`}
                >
                  <div className="flex items-center space-x-2.5 min-w-0">
                    <Icon
                      className={`w-4 h-4 shrink-0 ${
                        isActive ? "text-amber-400" : "text-slate-400"
                      }`}
                    />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded-full uppercase shrink-0 ${
                        isActive
                          ? "bg-amber-500 text-slate-950"
                          : "bg-slate-800 text-slate-400 border border-slate-700"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Recent Consultations Section */}
        <div>
          <div className="flex items-center justify-between px-3">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              {t("nav.recent_consultations", "Recent Consultations")}
            </p>
            {recentConsultations.length > 0 && (
              <button
                onClick={handleClearHistory}
                title="Clear recent history"
                className="text-[10px] text-slate-500 hover:text-rose-400 transition-colors p-1"
                aria-label="Clear recent consultations"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            )}
          </div>

          <div className="mt-2 space-y-1">
            {recentConsultations.length === 0 ? (
              <div className="px-3 py-3 rounded-lg border border-dashed border-slate-800 text-[11px] text-slate-500 text-center">
                <MessageSquare className="w-4 h-4 mx-auto mb-1 text-slate-600" />
                <span>{t("nav.no_recent", "No recent consultations")}</span>
              </div>
            ) : (
              recentConsultations.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleRecentClick(item.query)}
                  className="w-full text-left flex items-start space-x-2 px-3 py-2 rounded-lg text-xs text-slate-300 hover:bg-slate-800/70 hover:text-white transition-colors group"
                >
                  <MessageSquare className="w-3.5 h-3.5 mt-0.5 text-amber-500/70 group-hover:text-amber-400 shrink-0" />
                  <span className="truncate flex-1 font-normal text-[11px]">
                    {item.query}
                  </span>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Support & System Help */}
        <div>
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            {t("nav.help_title", "Help & Official Portals")}
          </p>
          <div className="mt-2 space-y-1">
            <Link
              href="/about"
              onClick={onCloseMobile}
              className={`flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-colors ${
                pathname === "/about"
                  ? "bg-[#152E4D] text-white font-semibold"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <Info className="w-4 h-4 text-slate-400" />
              <span>{t("nav.about", "About & Support")}</span>
            </Link>

            <a
              href="https://www.bis.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-slate-800/50 transition-colors"
            >
              <span className="truncate">Official BIS Portal</span>
              <ExternalLink className="w-3 h-3 text-slate-500 shrink-0" />
            </a>

            <a
              href="https://www.manakonline.in"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white hover:bg-slate-800/50 transition-colors"
            >
              <span className="truncate">Manakonline e-Portal</span>
              <ExternalLink className="w-3 h-3 text-slate-500 shrink-0" />
            </a>
          </div>
        </div>
      </div>

      {/* Language & Identity Footer */}
      <div className="p-4 border-t border-slate-800 bg-[#060f1c] space-y-2">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 text-slate-400">
            <Globe className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-[11px] font-medium">
              {language === "hi"
                ? "हिन्दी सक्रिय"
                : language === "ta"
                ? "தமிழ் செயலில்"
                : "English Active"}
            </span>
          </div>
          <span className="text-[10px] text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-800/50 px-1.5 py-0.5 rounded-xs">
            Groq LPU
          </span>
        </div>
        <p className="text-[10px] text-slate-400">
          SIH 2026 Problem Statement #107
        </p>
      </div>
    </aside>
  );
}
