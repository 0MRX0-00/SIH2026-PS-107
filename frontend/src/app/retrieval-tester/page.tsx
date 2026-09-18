"use client";

import React, { useState } from "react";
import {
  Search,
  Database,
  Layers,
  FileCheck2,
  Filter,
  CheckCircle2,
  BookOpen,
  ArrowRight,
  Code2,
  Bot,
  ShieldCheck,
  Clock,
  AlertTriangle,
  Sparkles,
} from "lucide-react";
import {
  searchKnowledgeBase,
  RetrievalSearchResponse,
  fetchChatDebug,
  ChatDebugResponse,
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

export default function RetrievalTesterPage() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<"rag" | "retrieval">("rag");

  // RAG Inspector State
  const [ragQuery, setRagQuery] = useState(
    "What are the standard ratings and pin configurations for plugs in IS 1293:2019?"
  );
  const [ragTopK, setRagTopK] = useState(4);
  const [ragStandardFilter, setRagStandardFilter] = useState("");
  const [ragLoading, setRagLoading] = useState(false);
  const [ragResponse, setRagResponse] = useState<ChatDebugResponse | null>(null);
  const [ragError, setRagError] = useState<string | null>(null);

  // Raw Retrieval State
  const [retrievalQuery, setRetrievalQuery] = useState(
    "What are the standard ratings for electrical plugs and sockets?"
  );
  const [retrievalTopK, setRetrievalTopK] = useState(5);
  const [retrievalFilter, setRetrievalFilter] = useState("");
  const [retrievalLoading, setRetrievalLoading] = useState(false);
  const [retrievalResponse, setRetrievalResponse] = useState<RetrievalSearchResponse | null>(null);
  const [retrievalError, setRetrievalError] = useState<string | null>(null);

  const handleRagSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;

    setRagLoading(true);
    setRagError(null);
    try {
      const res = await fetchChatDebug(
        ragQuery,
        [],
        ragTopK,
        ragStandardFilter || undefined
      );
      setRagResponse(res);
    } catch (err: any) {
      setRagError(err.message || "RAG pipeline debug request failed.");
    } finally {
      setRagLoading(false);
    }
  };

  const handleRetrievalSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!retrievalQuery.trim()) return;

    setRetrievalLoading(true);
    setRetrievalError(null);
    try {
      const res = await searchKnowledgeBase(
        retrievalQuery,
        retrievalTopK,
        retrievalFilter || undefined
      );
      if (res) {
        setRetrievalResponse(res);
      } else {
        setRetrievalError("Retrieval request returned empty.");
      }
    } catch (err: any) {
      setRetrievalError(err.message || "An error occurred during vector retrieval.");
    } finally {
      setRetrievalLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-bis-blue" />
            <h1 className="text-xl font-bold text-slate-900">
              {t("retrieval_tester.title", "RAG & Retrieval Inspector")}
            </h1>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded">
              {t("retrieval_tester.phase_badge", "Phase 3 Developer Tool")}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {t("retrieval_tester.subtitle", "Audit and verify vector retrieval, context building, Groq LPU inference, and citation validation in real time.")}
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
          <button
            onClick={() => setActiveTab("rag")}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all flex items-center space-x-1.5 ${
              activeTab === "rag"
                ? "bg-white text-bis-blue shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Bot className="w-3.5 h-3.5" />
            <span>{t("retrieval_tester.tab_full_rag", "Full RAG Inspector")}</span>
          </button>
          <button
            onClick={() => setActiveTab("retrieval")}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all flex items-center space-x-1.5 ${
              activeTab === "retrieval"
                ? "bg-white text-bis-blue shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{t("retrieval_tester.tab_raw_vector", "Raw Vector Search")}</span>
          </button>
        </div>
      </div>

      {activeTab === "rag" ? (
        /* RAG INSPECTOR TAB */
        <div className="space-y-6">
          <form
            onSubmit={handleRagSearch}
            className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4"
          >
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                {t("retrieval_tester.rag_query_label", "RAG Test Query")}
              </label>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  placeholder="e.g. What are the testing parameters for IS 1293?"
                  className="w-full pl-9 pr-4 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white text-slate-900"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  {t("retrieval_tester.top_k_label", "Top-K Evidence Chunks")}
                </label>
                <select
                  value={ragTopK}
                  onChange={(e) => setRagTopK(Number(e.target.value))}
                  className="w-full py-2 px-3 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-700"
                >
                  <option value={2}>2 {t("retrieval_tester.chunks_count", "Chunks")}</option>
                  <option value={4}>4 {t("retrieval_tester.chunks_count", "Chunks")} ({t("retrieval_tester.recommended", "Recommended")})</option>
                  <option value={6}>6 {t("retrieval_tester.chunks_count", "Chunks")}</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  {t("retrieval_tester.standard_filter_label", "Standard Filter (Optional)")}
                </label>
                <input
                  type="text"
                  value={ragStandardFilter}
                  onChange={(e) => setRagStandardFilter(e.target.value)}
                  placeholder="e.g. IS 1293:2019"
                  className="w-full py-2 px-3 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-700"
                />
              </div>

              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={ragLoading}
                  className="w-full bg-bis-blue hover:bg-blue-900 disabled:bg-slate-400 text-white font-bold py-2 px-4 rounded-lg text-xs transition-all shadow-sm flex items-center justify-center space-x-2 h-[34px]"
                >
                  {ragLoading ? (
                    <span>{t("retrieval_tester.btn_executing", "Executing RAG Trace...")}</span>
                  ) : (
                    <>
                      <span>{t("retrieval_tester.btn_inspect_trace", "Inspect Full RAG Trace")}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>

          {ragError && (
            <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs">
              <p className="font-bold">RAG Debug Error:</p>
              <p>{ragError}</p>
            </div>
          )}

          {ragResponse && (
            <div className="space-y-6">
              {/* Timing & Summary Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm text-center">
                  <span className="text-[10px] text-slate-400 block uppercase">{t("retrieval_tester.timing_retrieval", "Retrieval")}</span>
                  <span className="text-xs font-bold font-mono text-slate-800">
                    {ragResponse.timing.retrieval_ms}ms
                  </span>
                </div>
                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm text-center">
                  <span className="text-[10px] text-slate-400 block uppercase">{t("retrieval_tester.timing_context", "Context Assembly")}</span>
                  <span className="text-xs font-bold font-mono text-slate-800">
                    {ragResponse.timing.context_assembly_ms}ms
                  </span>
                </div>
                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm text-center">
                  <span className="text-[10px] text-slate-400 block uppercase">{t("retrieval_tester.timing_groq", "Groq Inference")}</span>
                  <span className="text-xs font-bold font-mono text-slate-800">
                    {ragResponse.timing.groq_ms}ms
                  </span>
                </div>
                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm text-center">
                  <span className="text-[10px] text-slate-400 block uppercase">{t("retrieval_tester.timing_citation", "Citation Check")}</span>
                  <span className="text-xs font-bold font-mono text-slate-800">
                    {ragResponse.timing.citation_validation_ms}ms
                  </span>
                </div>
                <div className="bg-emerald-50 p-3 rounded-lg border border-emerald-200 shadow-sm text-center col-span-2 sm:col-span-1">
                  <span className="text-[10px] text-emerald-600 block uppercase font-semibold">{t("retrieval_tester.timing_total", "Total Latency")}</span>
                  <span className="text-xs font-bold font-mono text-emerald-800">
                    {ragResponse.timing.total_ms}ms
                  </span>
                </div>
              </div>

              {/* Final Answer & Validated Citations */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center space-x-2">
                    <ShieldCheck className="w-5 h-5 text-emerald-600" />
                    <h2 className="text-sm font-bold text-slate-900">
                      {t("retrieval_tester.grounded_answer_title", "Grounded Answer & Validated Citations")}
                    </h2>
                  </div>
                  <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                    Model: {ragResponse.model}
                  </span>
                </div>

                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs text-slate-800 whitespace-pre-wrap leading-relaxed">
                  {ragResponse.final_answer}
                </div>

                {/* Validated Citations */}
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
                    <BookOpen className="w-3.5 h-3.5 text-bis-blue" />
                    <span>{t("retrieval_tester.validated_citations_title", "Validated Citations")} ({ragResponse.validated_citations.length})</span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {ragResponse.validated_citations.map((c, i) => (
                      <div key={i} className="bg-blue-50/60 p-3 rounded-lg border border-blue-200 text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-bis-blue">
                            [{c.id}] {c.standard_number}
                          </span>
                          <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-mono">
                            Cl. {c.clause || "Gen"}
                          </span>
                        </div>
                        {c.reason && (
                          <p className="text-[11px] text-slate-600 italic">&quot;{c.reason}&quot;</p>
                        )}
                        <p className="text-[10px] text-slate-500 font-mono line-clamp-2">{c.snippet}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Rejected Citations (if any) */}
                {ragResponse.rejected_citations && ragResponse.rejected_citations.length > 0 && (
                  <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-xs text-amber-900 space-y-1">
                    <div className="flex items-center space-x-1.5 font-bold">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      <span>{t("retrieval_tester.rejected_citations_title", "Rejected Hallucinated Citations (Stripped by Backend)")}</span>
                    </div>
                    {ragResponse.rejected_citations.map((rej, idx) => (
                      <p key={idx} className="text-[11px] text-amber-800">
                        • Citation ID [{rej.id || "Unknown"}]: {rej.reason}
                      </p>
                    ))}
                  </div>
                )}
              </div>

              {/* Intermediate Context & Prompts Accordion */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
                  <Code2 className="w-3.5 h-3.5 text-slate-600" />
                  <span>{t("retrieval_tester.assembled_context_title", "Assembled Evidence Context (Prompt Injection Isolated)")}</span>
                </h3>
                <div className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-[11px] leading-relaxed max-h-60 overflow-y-auto whitespace-pre-wrap">
                  {ragResponse.assembled_context}
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* RAW VECTOR SEARCH TAB */
        <div className="space-y-6">
          <form
            onSubmit={handleRetrievalSearch}
            className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4"
          >
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                {t("retrieval_tester.raw_search_query_label", "Vector Search Query")}
              </label>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={retrievalQuery}
                  onChange={(e) => setRetrievalQuery(e.target.value)}
                  placeholder="e.g. What are the testing parameters for IS 1293?"
                  className="w-full pl-9 pr-4 py-2.5 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue focus:bg-white text-slate-900"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  {t("retrieval_tester.top_k_chunks_label", "Top-K Chunks")}
                </label>
                <select
                  value={retrievalTopK}
                  onChange={(e) => setRetrievalTopK(Number(e.target.value))}
                  className="w-full py-2 px-3 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-700"
                >
                  <option value={3}>3 {t("retrieval_tester.chunks_count", "Chunks")}</option>
                  <option value={5}>5 {t("retrieval_tester.chunks_count", "Chunks")}</option>
                  <option value={10}>10 {t("retrieval_tester.chunks_count", "Chunks")}</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  {t("retrieval_tester.standard_filter_raw", "Standard Filter")}
                </label>
                <input
                  type="text"
                  value={retrievalFilter}
                  onChange={(e) => setRetrievalFilter(e.target.value)}
                  placeholder="e.g. IS 1293:2019"
                  className="w-full py-2 px-3 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-bis-blue text-slate-700"
                />
              </div>

              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={retrievalLoading}
                  className="w-full bg-bis-blue hover:bg-blue-900 disabled:bg-slate-400 text-white font-bold py-2 px-4 rounded-lg text-xs transition-all shadow-sm flex items-center justify-center space-x-2 h-[34px]"
                >
                  {retrievalLoading ? (
                    <span>{t("retrieval_tester.btn_retrieving_vectors", "Retrieving Vectors...")}</span>
                  ) : (
                    <>
                      <span>{t("retrieval_tester.btn_exec_vector_search", "Execute Vector Search")}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>

          {retrievalError && (
            <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs">
              <p className="font-bold">Retrieval Error:</p>
              <p>{retrievalError}</p>
            </div>
          )}

          {retrievalResponse && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                  <FileCheck2 className="w-4 h-4 text-emerald-600" />
                  <span>{t("retrieval_tester.retrieved_chunks_title", "Retrieved Evidence Chunks")} ({retrievalResponse.total_results} results)</span>
                </h2>
                <span className="text-[11px] font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                  {retrievalResponse.retrieval_mode}
                </span>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {retrievalResponse.results.map((item, idx) => (
                  <div
                    key={idx}
                    className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:border-blue-300 transition-all space-y-3"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold bg-blue-50 text-bis-blue px-2 py-0.5 rounded font-mono">
                          #{idx + 1} {item.standard_number || "IS METADATA"}
                        </span>
                        {item.clause && (
                          <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-semibold">
                            {item.clause}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-3 text-xs">
                        <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          {t("retrieval_tester.score_label", "Score:")} {(item.score * 100).toFixed(1)}%
                        </span>
                        <span className="text-slate-400">
                          {t("retrieval_tester.page_label", "Page:")} {item.page_start ?? "N/A"}
                        </span>
                      </div>
                    </div>

                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 font-mono text-xs text-slate-800 whitespace-pre-wrap leading-relaxed">
                      {item.text}
                    </div>

                    <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-1">
                      <span>{t("retrieval_tester.source_label", "Source:")} {item.source || "Bureau of Indian Standards"}</span>
                      <span className="font-mono text-[10px]">{t("retrieval_tester.chunk_id_label", "Chunk ID:")} {item.chunk_id}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

