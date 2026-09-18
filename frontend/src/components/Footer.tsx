"use client";

import React from "react";
import Link from "next/link";
import { Shield, ExternalLink, Info, Award, FileSearch, FlaskConical, BotMessageSquare } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="bg-slate-900 text-slate-400 text-xs border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-2 space-y-2">
            <div className="flex items-center space-x-2 text-white font-semibold">
              <Shield className="w-5 h-5 text-bis-saffron" />
              <span className="text-sm font-bold">e-BIS Sahayak</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed max-w-md">
              {t(
                "footer.tagline",
                "Your intelligent assistant for Indian Standards, BIS certification guidance, and testing laboratory discovery. Grounded in authoritative BIS documentation."
              )}
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-2.5 text-xs uppercase tracking-wider">
              {t("footer.navigation_title", "Services")}
            </h4>
            <ul className="space-y-1.5 text-xs">
              <li><Link href="/" className="hover:text-white transition-colors">{t("nav.dashboard", "Home")}</Link></li>
              <li><Link href="/assistant" className="hover:text-white transition-colors">{t("nav.assistant", "Sahayak Assistant")}</Link></li>
              <li><Link href="/standards" className="hover:text-white transition-colors">{t("nav.standards", "Standards Explorer")}</Link></li>
              <li><Link href="/certification" className="hover:text-white transition-colors">{t("nav.certification", "Certification Guidance")}</Link></li>
              <li><Link href="/laboratories" className="hover:text-white transition-colors">{t("nav.laboratories", "Testing Laboratories")}</Link></li>
              <li><Link href="/about" className="hover:text-white transition-colors">{t("nav.about", "About e-BIS Sahayak")}</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-2.5 text-xs uppercase tracking-wider">
              {t("footer.official_links_title", "Official BIS Portals")}
            </h4>
            <ul className="space-y-1.5 text-xs">
              <li>
                <a href="https://www.bis.gov.in" target="_blank" rel="noreferrer" className="flex items-center space-x-1 hover:text-white transition-colors">
                  <span>Bureau of Indian Standards</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://www.manakonline.in" target="_blank" rel="noreferrer" className="flex items-center space-x-1 hover:text-white transition-colors">
                  <span>e-BIS / ManakOnline Portal</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
              <li>
                <a href="https://www.services.bis.gov.in" target="_blank" rel="noreferrer" className="flex items-center space-x-1 hover:text-white transition-colors">
                  <span>BIS Conformity Assessment Services</span>
                  <ExternalLink className="w-3 h-3 text-slate-500" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-8 pt-4 flex flex-col sm:flex-row justify-between items-center text-[11px] text-slate-500 gap-2">
          <p>© 2026 e-BIS Sahayak. {t("footer.copyright_note", "Grounded Information & Guidance System.")}</p>
          <p>{t("footer.disclaimer_note", "For formal licensing and fee payments, visit the official ManakOnline portal.")}</p>
        </div>
      </div>
    </footer>
  );
}
