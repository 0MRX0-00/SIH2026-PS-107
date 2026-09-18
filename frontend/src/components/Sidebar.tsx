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
  ShieldCheck
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export function Sidebar() {
  const pathname = usePathname();
  const { t, language } = useLanguage();

  const NAV_ITEMS = [
    { href: "/", label: t("nav.dashboard", "Dashboard"), icon: LayoutDashboard },
    { href: "/assistant", label: t("nav.assistant", "Sahayak Assistant"), icon: BotMessageSquare },
    { href: "/standards", label: t("nav.standards", "Standards Explorer"), icon: FileSearch },
    { href: "/certification", label: t("nav.certification", "Certification Guidance"), icon: Award },
    { href: "/laboratories", label: t("nav.laboratories", "Testing Laboratories"), icon: FlaskConical },
    { href: "/about", label: t("nav.about", "About e-BIS Sahayak"), icon: Info },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-85px)] p-4 flex flex-col justify-between hidden md:flex">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            {t("nav.services_title", "Services & Features")}
          </p>
          <nav className="mt-2 space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-blue-50 text-bis-blue font-bold border border-blue-200 shadow-xs"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? "text-bis-blue" : "text-slate-500"}`} />
                    <span>{item.label}</span>
                  </div>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Multilingual Status Card */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-600 space-y-1.5">
          <div className="flex items-center space-x-1.5 font-bold text-slate-800">
            <Globe className="w-3.5 h-3.5 text-bis-blue" />
            <span>{t("nav.multilingual_active", "Active Language")}</span>
          </div>
          <p className="text-[11px] leading-relaxed">
            {t("nav.multilingual_desc", "Information and guidance available in")}{" "}
            <strong>{language === "hi" ? "हिन्दी" : language === "ta" ? "தமிழ்" : "English"}</strong>.
          </p>
        </div>
      </div>

      <div className="text-xs text-slate-400 border-t border-slate-200 pt-3 space-y-1">
        <p className="font-semibold text-slate-600">{t("nav.portal_name", "e-BIS Sahayak Portal")}</p>
        <p className="text-[11px] text-slate-500">{t("nav.portal_tagline", "Indian Standards Information Assistant")}</p>
      </div>
    </aside>
  );
}
