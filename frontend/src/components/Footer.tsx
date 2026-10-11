"use client";

import React from "react";
import Link from "next/link";
import { ShieldCheck, ExternalLink, Globe } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="bg-white border-t border-slate-200 text-xs text-slate-500 mt-auto py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2 text-slate-700">
          <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0" />
          <span className="font-semibold text-slate-900">e-BIS Sahayak</span>
          <span className="text-slate-300">•</span>
          <span className="text-slate-500 text-[11px]">
            {t("footer.bis_tagline", "Indian Standards Regulatory Information & Guidance Assistant")}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] text-slate-600">
          <a
            href="https://www.bis.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-amber-600 flex items-center space-x-1 transition-colors"
          >
            <span>Official BIS Portal</span>
            <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
          </a>
          <a
            href="https://www.manakonline.in"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-amber-600 flex items-center space-x-1 transition-colors"
          >
            <span>Manakonline e-Portal</span>
            <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
          </a>
          <a
            href="https://lims.bis.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-amber-600 flex items-center space-x-1 transition-colors"
          >
            <span>BIS LIMS Labs</span>
            <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
          </a>
          <Link href="/about" className="hover:text-amber-600 transition-colors">
            {t("nav.about", "About & Support")}
          </Link>
        </div>
      </div>

      <div className="max-w-7xl mx-auto mt-4 pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-2 text-[10px] text-slate-400">
        <p>
          © 2026 Bureau of Indian Standards (BIS) • e-BIS Sahayak AI (SIH 2026 PS #107).
        </p>
        <p>
          Responses are source-grounded guidance. For formal statutory applications, refer to official BIS orders.
        </p>
      </div>
    </footer>
  );
}
