"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BotMessageSquare,
  FileSearch,
  Award,
  FlaskConical,
  Info,
  Globe,
  ShieldCheck,
  Zap,
  CheckCircle2,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export function Sidebar() {
  const pathname = usePathname();
  const { t, language } = useLanguage();

  const NAV_ITEMS = [
    { href: "/", label: t("nav.dashboard", "Dashboard"), icon: LayoutDashboard, badge: null },
    { href: "/assistant", label: t("nav.assistant", "Sahayak Assistant"), icon: BotMessageSquare, badge: "AI" },
    { href: "/standards", label: t("nav.standards", "Standards Explorer"), icon: FileSearch, badge: null },
    { href: "/certification", label: t("nav.certification", "Certification Guidance"), icon: Award, badge: "Wizard" },
    { href: "/laboratories", label: t("nav.laboratories", "Testing Laboratories"), icon: FlaskConical, badge: null },
    { href: "/about", label: t("nav.about", "About e-BIS Sahayak"), icon: Info, badge: null },
  ];

  return (
    <aside className="w-64 bg-slate-900/50 backdrop-blur-md border-r border-slate-200/80 min-h-[calc(100vh-85px)] p-4 flex flex-col justify-between hidden md:flex shrink-0">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
            {t("nav.services_title", "Services & Features")}
          </p>
          <nav className="mt-2.5 space-y-1.5">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-blue-900/10 text-blue-900 border border-blue-200 font-bold shadow-xs"
                      : "text-slate-600 hover:bg-slate-200/60 hover:text-slate-900"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? "text-blue-700" : "text-slate-400"}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded-full uppercase ${
                        isActive
                          ? "bg-amber-500 text-slate-950"
                          : "bg-slate-200 text-slate-600"
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

        {/* Multilingual Status Card */}
        <div className="bg-gradient-to-br from-slate-900 to-blue-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-300 space-y-2 shadow-sm">
          <div className="flex items-center space-x-2 font-bold text-white">
            <Globe className="w-4 h-4 text-amber-400" />
            <span>{t("nav.multilingual_active", "Active Language")}</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            {t("nav.multilingual_desc", "Information and guidance available in")}{" "}
            <strong className="text-amber-400">
              {language === "hi" ? "हिन्दी (Hindi)" : language === "ta" ? "தமிழ் (Tamil)" : "English"}
            </strong>.
          </p>
          <div className="flex items-center space-x-1.5 text-[10px] text-emerald-400 font-medium pt-1 border-t border-slate-800">
            <CheckCircle2 className="w-3 h-3 shrink-0" />
            <span>100% Multilingual Key Parity</span>
          </div>
        </div>
      </div>

      {/* Footer Identity Pill */}
      <div className="text-xs text-slate-500 border-t border-slate-200 pt-3 space-y-1">
        <div className="flex items-center space-x-1.5 text-slate-700 font-bold">
          <ShieldCheck className="w-4 h-4 text-amber-500" />
          <span>{t("nav.portal_name", "e-BIS Sahayak Portal")}</span>
        </div>
        <p className="text-[11px] text-slate-500">{t("nav.portal_tagline", "Indian Standards Information Assistant")}</p>
      </div>
    </aside>
  );
}
