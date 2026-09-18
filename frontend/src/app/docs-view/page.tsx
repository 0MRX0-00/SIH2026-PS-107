"use client";

import React from "react";
import { BookOpen, FileText, CheckCircle2, Shield, Layers, Database, Lock, Cpu } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function DocsViewPage() {
  const { t } = useLanguage();

  const DOCS_LIST = [
    {
      file: "problem-statement.md",
      title: t("docs_view.problem_statement_title", "Problem Statement (SIH26107)"),
      icon: Shield,
      desc: t("docs_view.problem_statement_desc", "Context, challenges, and core objectives for e-BIS Sahayak."),
    },
    {
      file: "requirements.md",
      title: t("docs_view.requirements_title", "System Requirements"),
      icon: CheckCircle2,
      desc: t("docs_view.requirements_desc", "Functional (FR) & non-functional (NFR) engineering requirements."),
    },
    {
      file: "architecture.md",
      title: t("docs_view.architecture_title", "System Architecture"),
      icon: Layers,
      desc: t("docs_view.architecture_desc", "Decoupled multi-tier services, vector search, and LLM orchestration."),
    },
    {
      file: "technology-stack.md",
      title: t("docs_view.technology_stack_title", "Technology Stack"),
      icon: Cpu,
      desc: t("docs_view.technology_stack_desc", "FastAPI, Next.js, PostgreSQL, Qdrant, Groq, and rationale."),
    },
    {
      file: "database-design.md",
      title: t("docs_view.database_design_title", "Database & Schema Design"),
      icon: Database,
      desc: t("docs_view.database_design_desc", "PostgreSQL tables with deep citation and source traceability."),
    },
    {
      file: "api-design.md",
      title: t("docs_view.api_design_title", "API Design Specification"),
      icon: FileText,
      desc: t("docs_view.api_design_desc", "OpenAPI endpoints, versioning strategy, and response structures."),
    },
    {
      file: "rag-architecture.md",
      title: t("docs_view.rag_architecture_title", "Grounded RAG Pipeline"),
      icon: Layers,
      desc: t("docs_view.rag_architecture_desc", "Hierarchical clause chunking, hybrid retrieval, and prompt guardrails."),
    },
    {
      file: "security.md",
      title: t("docs_view.security_title", "Security Foundation"),
      icon: Lock,
      desc: t("docs_view.security_desc", "Zero-secrets architecture, CORS policies, and injection defenses."),
    },
    {
      file: "development-phases.md",
      title: t("docs_view.development_phases_title", "Development Phases Roadmap"),
      icon: BookOpen,
      desc: t("docs_view.development_phases_desc", "Phase 1 Foundation through Phase 7 Production hardening."),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-bis-blue" />
          <h1 className="text-xl font-bold text-slate-900">
            {t("docs_view.title", "System Documentation & Engineering Specs")}
          </h1>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {t("docs_view.subtitle", "Complete technical specifications and design blueprints located under the docs/ directory.")}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {DOCS_LIST.map((doc) => {
          const Icon = doc.icon;
          return (
            <div
              key={doc.file}
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:border-blue-300 transition-all space-y-2"
            >
              <div className="flex items-center space-x-2 text-bis-blue">
                <Icon className="w-4 h-4" />
                <h2 className="font-bold text-sm text-slate-900">{doc.title}</h2>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                {doc.desc}
              </p>
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>docs/{doc.file}</span>
                <span className="text-emerald-600 font-sans font-semibold">
                  {t("docs_view.available", "Available")}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

