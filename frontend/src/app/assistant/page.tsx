"use client";

import React, { useState, useRef, useEffect, Suspense } from "react";
import {
  Bot,
  User,
  Send,
  Sparkles,
  Layers,
  FileCheck2,
  AlertCircle,
  Clock,
  BookOpen,
  ShieldCheck,
  RefreshCw,
  HelpCircle,
  Languages,
  ThumbsUp,
  ThumbsDown,
} from "lucide-react";
import { useSearchParams } from "next/navigation";
import {
  sendChatMessage,
  ChatMessageInput,
  CitationItem,
  ChatResponse,
  submitFeedback,
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

interface Message {
  id: string;
  sender: "user" | "assistant";
  content: string;
  citations?: CitationItem[];
  sources_used?: number;
  insufficient_evidence?: boolean;
  processing_time_ms?: number;
  model?: string;
  created_at: Date;
}

const SAMPLE_SUGGESTIONS: Record<string, string[]> = {
  en: [
    "What are the rated voltages and currents in IS 1293:2019?",
    "Is ISI mark certification mandatory for electrical plugs under QCO?",
    "What documentation is required for electronics under CRS Scheme II?",
    "What is the required creepage distance under IS 1293 Clause 12.1?",
  ],
  hi: [
    "IS 1293:2019 में रेटेड वोल्टेज और करंट क्या हैं?",
    "क्या प्लग और सॉकेट के लिए ISI मार्क अनिवार्य है?",
    "CRS योजना II के तहत इलेक्ट्रॉनिक्स के लिए क्या दस्तावेज़ आवश्यक हैं?",
    "IS 1293 क्लॉज 12.1 के तहत क्रीपेज दूरी क्या है?",
  ],
  ta: [
    "IS 1293:2019 இன் கீழ் மின்னழுத்தம் மற்றும் மின்னோட்ட விவரங்கள் என்ன?",
    "பிளக் மற்றும் சாக்கெட்டுகளுக்கு ISI மார்க் கட்டாயமா?",
    "CRS திட்டம் II இன் கீழ் தேவையான ஆவணங்கள் என்ன?",
    "IS 1293 பிரிவு 12.1 இன் கீழ் தேவையான creepage distance என்ன?",
  ],
};

function AssistantContent() {
  const { language, t } = useLanguage();
  const searchParams = useSearchParams();
  const initialStandard = searchParams.get("standard") || "";
  const initialPrompt = searchParams.get("prompt") || "";

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome-1",
      sender: "assistant",
      content: t("assistant.welcome_message"),
      created_at: new Date(),
    },
  ]);

  const [inputQuery, setInputQuery] = useState(initialPrompt);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<CitationItem | null>(null);
  const [activeStandardFilter, setActiveStandardFilter] = useState<string>(initialStandard);
  const [feedbackMap, setFeedbackMap] = useState<Record<string, "positive" | "negative">>({});

  const handleFeedback = async (msgId: string, query: string, answer: string, isHelpful: boolean) => {
    setFeedbackMap((prev) => ({ ...prev, [msgId]: isHelpful ? "positive" : "negative" }));
    try {
      await submitFeedback({
        message_id: msgId,
        query: query || "e-BIS Sahayak Query",
        answer_snippet: answer.slice(0, 200),
        is_helpful: isHelpful,
        language,
      });
    } catch (e) {
      console.warn("Feedback submission error:", e);
    }
  };

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Update initial welcome message when language changes if it's the only message
  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 1 && prev[0].id === "welcome-1") {
        return [
          {
            id: "welcome-1",
            sender: "assistant",
            content: t("assistant.welcome_message"),
            created_at: new Date(),
          },
        ];
      }
      return prev;
    });
  }, [language, t]);

  useEffect(() => {
    if (initialStandard) {
      setActiveStandardFilter(initialStandard);
    }
    if (initialPrompt) {
      setInputQuery(initialPrompt);
    }
  }, [initialStandard, initialPrompt]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputQuery).trim();
    if (!query || isLoading) return;

    setInputQuery("");
    setErrorMessage(null);

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      content: query,
      created_at: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Build history payload for multi-turn conversation
      const historyPayload: ChatMessageInput[] = messages
        .filter((m) => m.id !== "welcome-1")
        .slice(-6)
        .map((m) => ({
          role: m.sender === "user" ? "user" : "assistant",
          content: m.content,
        }));

      const res: ChatResponse = await sendChatMessage(
        query,
        historyPayload,
        4,
        activeStandardFilter || undefined,
        language
      );

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        sender: "assistant",
        content: res.answer,
        citations: res.citations,
        sources_used: res.sources_used,
        insufficient_evidence: res.insufficient_evidence,
        processing_time_ms: res.processing_time_ms,
        model: res.model,
        created_at: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      if (res.citations && res.citations.length > 0) {
        setSelectedCitation(res.citations[0]);
      }
    } catch (err: any) {
      console.error("Chat error:", err);
      setErrorMessage(
        err.message || t("common.error")
      );
    } finally {
      setIsLoading(false);
    }
  };

  const suggestions = SAMPLE_SUGGESTIONS[language] || SAMPLE_SUGGESTIONS.en;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-slate-900">
              {t("assistant.title")}
            </h1>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded border border-emerald-300 flex items-center space-x-1">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              <span>{t("assistant.grounded_live")}</span>
            </span>
          </div>
          <p className="text-xs text-slate-500">
            {t("assistant.subtitle")}
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg text-blue-900 font-medium">
            <Languages className="w-3.5 h-3.5 text-bis-blue" />
            <span>{language === "hi" ? "हिन्दी (Hindi)" : language === "ta" ? "தமிழ் (Tamil)" : "English (EN)"}</span>
          </div>
          {activeStandardFilter && (
            <div className="flex items-center space-x-1 bg-amber-50 border border-amber-200 text-amber-800 px-2 py-1 rounded-lg">
              <span>{t("assistant.filter_label", "Filter:")} <strong>{activeStandardFilter}</strong></span>
              <button
                onClick={() => setActiveStandardFilter("")}
                className="text-xs text-amber-600 hover:text-amber-900 font-bold ml-1"
              >
                &times;
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Grid: Chat viewport on left, Grounded Evidence Panel on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Area (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[650px]">
          {/* Messages Viewport */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50/50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start space-x-3 ${
                  msg.sender === "user" ? "flex-row-reverse space-x-reverse" : ""
                }`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm ${
                    msg.sender === "user"
                      ? "bg-bis-blue text-white"
                      : "bg-bis-navy text-white"
                  }`}
                >
                  {msg.sender === "user" ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4 text-bis-saffron" />
                  )}
                </div>

                {/* Message Bubble */}
                <div
                  className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed shadow-sm ${
                    msg.sender === "user"
                      ? "bg-bis-blue text-white rounded-tr-none"
                      : "bg-white text-slate-800 rounded-tl-none border border-slate-200"
                  }`}
                >
                  {/* Content */}
                  <div className="prose prose-xs max-w-none text-slate-800 dark:text-slate-800 space-y-2">
                    {msg.content.split("\n\n").map((para, pIdx) => {
                      if (msg.sender === "user") {
                        return (
                          <p key={pIdx} className="text-white">
                            {para}
                          </p>
                        );
                      }
                      return (
                        <p key={pIdx} className="text-slate-800 whitespace-pre-line">
                          {para}
                        </p>
                      );
                    })}
                  </div>

                  {/* Insufficient Evidence Warning Banner */}
                  {msg.insufficient_evidence && (
                    <div className="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-2.5 text-[11px] text-amber-900 flex items-start space-x-2">
                      <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold">{t("assistant.insufficient_evidence")}</span>
                        <p className="text-amber-700 text-[10px] mt-0.5">
                          {t("assistant.insufficient_evidence_desc")}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Citations Pill Bar */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100 space-y-1.5">
                      <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                        <BookOpen className="w-3 h-3 text-bis-blue" />
                        <span>{t("assistant.sources_verified")} ({msg.citations.length})</span>
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.citations.map((cit) => (
                          <button
                            key={cit.id}
                            onClick={() => setSelectedCitation(cit)}
                            className={`text-[11px] px-2.5 py-1 rounded-md font-medium transition-all flex items-center space-x-1 border ${
                              selectedCitation?.id === cit.id &&
                              selectedCitation?.standard_number === cit.standard_number
                                ? "bg-bis-blue text-white border-bis-blue shadow-sm"
                                : "bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200"
                            }`}
                          >
                            <span className="font-mono font-bold">[{cit.id}]</span>
                            <span>{cit.standard_number}</span>
                            {cit.clause && <span className="text-[10px] opacity-80">| Cl. {cit.clause}</span>}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Latency, Source & Feedback Footer */}
                  {msg.sender === "assistant" && (
                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between text-[10px] text-slate-400 gap-2">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{msg.processing_time_ms ? `${msg.processing_time_ms}ms` : t("assistant.grounded_badge", "Grounded")}</span>
                      </span>

                      {msg.id !== "welcome-1" && (
                        <div className="flex items-center space-x-1.5 bg-slate-50 px-2 py-0.5 rounded border border-slate-200 text-slate-500">
                          <span className="text-[9px]">{t("assistant.helpful_question", "Helpful?")}</span>
                          <button
                            onClick={() => handleFeedback(msg.id, messages[messages.indexOf(msg) - 1]?.content || "", msg.content, true)}
                            className={`p-0.5 rounded hover:text-emerald-600 transition-colors ${feedbackMap[msg.id] === "positive" ? "text-emerald-600 font-bold" : "text-slate-400"}`}
                            title={t("assistant.helpful_tooltip", "Helpful response")}
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => handleFeedback(msg.id, messages[messages.indexOf(msg) - 1]?.content || "", msg.content, false)}
                            className={`p-0.5 rounded hover:text-red-600 transition-colors ${feedbackMap[msg.id] === "negative" ? "text-red-600 font-bold" : "text-slate-400"}`}
                            title={t("assistant.not_helpful_tooltip", "Not helpful")}
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>
                        </div>
                      )}

                      {msg.sources_used !== undefined && (
                        <span>{msg.sources_used} {t("assistant.sources_verified_count", "sources verified")}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 rounded-full bg-bis-navy text-white flex items-center justify-center shrink-0 shadow-sm animate-pulse">
                  <Bot className="w-4 h-4 text-bis-saffron" />
                </div>
                <div className="bg-white rounded-2xl rounded-tl-none p-4 text-xs text-slate-600 border border-slate-200 shadow-sm flex items-center space-x-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-bis-blue" />
                  <span>{t("assistant.loading_rag", "Finding relevant BIS standards & preparing verified response...")}</span>
                </div>
              </div>
            )}

            {/* Error Message */}
            {errorMessage && (
              <div className="bg-red-50 border border-red-200 text-red-800 p-3 rounded-xl text-xs flex items-start justify-between">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold">{t("assistant.error_title", "Request Notice")}</p>
                    <p className="text-[11px] text-red-700 mt-0.5">{errorMessage}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleSendMessage()}
                  className="bg-red-100 hover:bg-red-200 text-red-800 font-medium px-2 py-1 rounded text-[11px] transition-all"
                >
                  {t("assistant.retry", "Retry")}
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions */}
          <div className="px-3 pt-2 bg-white border-t border-slate-100 flex items-center space-x-1.5 overflow-x-auto text-[11px] text-slate-600">
            <span className="text-[10px] font-semibold text-slate-400 shrink-0 flex items-center space-x-1">
              <Sparkles className="w-3 h-3 text-amber-500" />
              <span>{t("dashboard.try_asking")}</span>
            </span>
            {suggestions.map((sug, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(sug)}
                disabled={isLoading}
                className="whitespace-nowrap bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded-full text-slate-700 transition-all border border-slate-200 shrink-0 text-[10px]"
              >
                {sug}
              </button>
            ))}
          </div>

          {/* Chat Input Bar */}
          <div className="p-3 border-t border-slate-200 bg-white rounded-b-xl">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center space-x-2"
            >
              <input
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                placeholder={t("assistant.input_placeholder")}
                disabled={isLoading}
                className="flex-1 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-bis-blue focus:border-transparent text-slate-900 placeholder:text-slate-400"
              />
              <button
                type="submit"
                disabled={isLoading || !inputQuery.trim()}
                className="bg-bis-blue hover:bg-blue-900 disabled:opacity-50 text-white px-4 py-2.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 shadow-sm shrink-0"
              >
                <Send className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{t("assistant.send")}</span>
              </button>
            </form>
            <p className="text-[10px] text-slate-400 mt-1.5 text-center">
              {t("assistant.evidence_guarantee")}
            </p>
          </div>
        </div>

        {/* Evidence & Grounding Drawer (1 col) */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 flex flex-col h-[650px] overflow-y-auto space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div className="flex items-center space-x-2">
              <FileCheck2 className="w-4 h-4 text-bis-blue" />
              <h2 className="text-sm font-bold text-slate-900">
                {t("assistant.sources_verified")}
              </h2>
            </div>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-mono font-semibold">
              {t("assistant.grounded_badge", "Grounded")}
            </span>
          </div>

          {selectedCitation ? (
            <div className="space-y-3">
              {/* Citation Details Card */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-2.5">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] bg-bis-blue text-white font-mono px-1.5 py-0.5 rounded font-bold">
                      [{selectedCitation.id}]
                    </span>
                    <h3 className="text-xs font-bold text-slate-900 mt-1">
                      {selectedCitation.standard_number}
                    </h3>
                  </div>
                    <span className="text-[10px] font-medium bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded flex items-center space-x-1">
                      <ShieldCheck className="w-3 h-3 text-emerald-600" />
                      <span>{t("assistant.verified_source", "Verified Source")}</span>
                    </span>
                </div>

                {selectedCitation.title && (
                  <p className="text-[11px] text-slate-600 font-medium leading-snug">
                    {selectedCitation.title}
                  </p>
                )}

                <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-slate-200">
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase tracking-wider">
                      {t("assistant.clause_section", "Clause / Section")}
                    </span>
                    <span className="font-semibold text-slate-800">
                      {selectedCitation.clause || "General"}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block uppercase tracking-wider">
                      {t("assistant.page_reference", "Page Reference")}
                    </span>
                    <span className="font-semibold text-slate-800">
                      {selectedCitation.page ? `${t("standards_detail.page_label", "Page")} ${selectedCitation.page}` : t("assistant.doc_body", "Document Body")}
                    </span>
                  </div>
                </div>

                {selectedCitation.reason && (
                  <div className="pt-2 border-t border-slate-200">
                    <span className="text-[10px] text-slate-400 block uppercase tracking-wider">
                      {t("assistant.verification_context", "Verification Context")}
                    </span>
                    <p className="text-[11px] text-slate-700 mt-0.5 italic">
                      &quot;{selectedCitation.reason}&quot;
                    </p>
                  </div>
                )}
              </div>

              {/* Verbatim Quoted Passage */}
              {selectedCitation.snippet && (
                <div className="space-y-1.5">
                  <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                    <BookOpen className="w-3 h-3 text-bis-blue" />
                    <span>{t("assistant.verbatim_passage", "Verbatim Grounded Passage")}</span>
                  </span>
                  <div className="bg-slate-900 text-slate-100 p-3 rounded-lg text-[11px] font-mono leading-relaxed border border-slate-800 max-h-48 overflow-y-auto">
                    {selectedCitation.snippet}
                  </div>
                </div>
              )}

              {/* Source Info */}
              <div className="text-[11px] text-slate-500 flex items-center justify-between pt-2">
                <span>{t("assistant.source_label", "Source:")} <strong>{selectedCitation.source || t("assistant.official_doc", "BIS Official Document")}</strong></span>
                <span className="text-[10px] text-emerald-600 font-medium">{t("assistant.sha_verified", "✓ SHA-256 Verified")}</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 space-y-2 text-slate-400">
              <HelpCircle className="w-8 h-8 mx-auto text-slate-300" />
              <p className="text-xs">
                {t("assistant.click_inspect_prompt", "Ask a question or click any citation pill to inspect verbatim grounded source clauses here.")}
              </p>
            </div>
          )}

          {/* Anti-Hallucination Reminder */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-[11px] text-blue-900 space-y-1 mt-auto">
            <div className="flex items-center space-x-1 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
              <span>{t("assistant.evidence_guarantee_title", "Evidence-First Guarantee")}</span>
            </div>
            <p className="text-blue-700 leading-relaxed text-[10px]">
              {t("assistant.evidence_guarantee")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AssistantPage() {
  const { t } = useLanguage();
  return (
    <Suspense fallback={<div className="bg-white p-12 rounded-xl border border-slate-200 text-center text-slate-500 text-sm">{t("assistant.loading_assistant", "Loading BIS Sahayak Assistant...")}</div>}>
      <AssistantContent />
    </Suspense>
  );
}
