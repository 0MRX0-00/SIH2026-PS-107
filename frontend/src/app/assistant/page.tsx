"use client";

import React, { useState, useRef, useEffect, Suspense } from "react";
import {
  Bot,
  User,
  Send,
  Sparkles,
  ShieldCheck,
  RefreshCw,
  HelpCircle,
  Languages,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  AlertCircle,
  Clock,
  BookOpen,
  ExternalLink,
  FileText,
} from "lucide-react";
import { useSearchParams } from "next/navigation";
import {
  sendChatMessage,
  ChatMessageInput,
  ChatResponse,
  submitFeedback,
  SourceItem,
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";

interface Message {
  id: string;
  sender: "user" | "assistant";
  content: string;
  sources?: SourceItem[];
  intent?: string;
  response_type?: string;
  clarification_needed?: boolean;
  clarification_options?: string[];
  evidence_status?: string;
  warnings?: string[];
  needs_clarification?: boolean;
  clarification_question?: string | null;
  processing_time_ms?: number;
  model?: string;
  created_at: Date;
}

const SAMPLE_SUGGESTIONS: Record<string, string[]> = {
  en: [
    "What are you used for?",
    "What is BIS certification?",
    "What certificates do I need to start an electronics business?",
    "What is CRS?",
    "What is IS 13252?",
    "Find BIS laboratories.",
  ],
  hi: [
    "आप किस काम आते हैं?",
    "बीआईएस प्रमाणन क्या है?",
    "इलेक्ट्रॉनिक्स व्यवसाय के लिए क्या प्रमाण पत्र चाहिए?",
    "CRS क्या है?",
    "IS 13252 के बारे में बताएं।",
    "बीआईएस मान्यता प्राप्त प्रयोगशालाएं खोजें।",
  ],
  ta: [
    "நீங்கள் என்ன செய்ய முடியும்?",
    "BIS சான்றிதழ் என்றால் என்ன?",
    "எலக்ட்ரானிக்ஸ் தொழிலுக்கு என்ன சான்றிதழ் தேவை?",
    "CRS என்றால் என்ன?",
    "IS 13252 பற்றி கூறுங்கள்.",
    "BIS ஆய்வகங்களை கண்டறியவும்.",
  ],
};

function AssistantContent() {
  const { language, t } = useLanguage();
  const searchParams = useSearchParams();
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
  const [loadingStep, setLoadingStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [feedbackMap, setFeedbackMap] = useState<Record<string, "positive" | "negative">>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopyMessage = (msgId: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

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

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < 2 ? prev + 1 : prev));
      }, 1500);
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

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
    if (initialPrompt) {
      setInputQuery(initialPrompt);
    }
  }, [initialPrompt]);

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
        language
      );

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        sender: "assistant",
        content: res.answer,
        sources: res.sources || res.citations || [],
        intent: res.intent,
        response_type: res.response_type,
        clarification_needed: res.clarification_needed || res.needs_clarification,
        clarification_options: res.clarification_options,
        evidence_status: res.evidence_status,
        warnings: res.warnings,
        needs_clarification: res.needs_clarification || res.clarification_needed,
        clarification_question: res.clarification_question,
        processing_time_ms: res.processing_time_ms,
        model: res.model,
        created_at: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
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

  const loadingMessages = [
    t("assistant.loading_step_1", "Understanding your question & context..."),
    t("assistant.loading_step_2", "Processing through Groq AI Assistant..."),
    t("assistant.loading_step_3", "Generating response..."),
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-slate-900">
              {t("assistant.title")}
            </h1>
            <span className="text-[10px] bg-blue-100 text-blue-800 font-semibold px-2 py-0.5 rounded border border-blue-300 flex items-center space-x-1">
              <Bot className="w-3 h-3 text-blue-600" />
              <span>Sahayak AI</span>
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
        </div>
      </div>

      {/* Main Grid: Chat viewport on left, Assistant Capabilities on right */}
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
                  {/* Evidence Status Badge Header */}
                  {msg.sender === "assistant" && msg.evidence_status && (
                    <div className="mb-2 flex items-center justify-between">
                      <span
                        className={`inline-flex items-center space-x-1 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          msg.evidence_status === "strong"
                            ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                            : msg.evidence_status === "limited"
                            ? "bg-amber-50 text-amber-800 border-amber-300"
                            : "bg-slate-100 text-slate-700 border-slate-300"
                        }`}
                      >
                        {msg.evidence_status === "strong" ? (
                          <ShieldCheck className="w-3 h-3 text-emerald-600" />
                        ) : msg.evidence_status === "limited" ? (
                          <AlertCircle className="w-3 h-3 text-amber-600" />
                        ) : (
                          <HelpCircle className="w-3 h-3 text-slate-500" />
                        )}
                        <span>
                          {msg.evidence_status === "strong"
                            ? "Strong Evidence"
                            : msg.evidence_status === "limited"
                            ? "Limited Evidence"
                            : "Insufficient Evidence"}
                        </span>
                      </span>
                    </div>
                  )}

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

                  {/* Evidence Warnings */}
                  {msg.warnings && msg.warnings.length > 0 && (
                    <div className="mt-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-2.5 text-[11px] space-y-1">
                      <div className="font-semibold flex items-center space-x-1 text-amber-900">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        <span>Evidence Warning</span>
                      </div>
                      {msg.warnings.map((w, wIdx) => (
                        <p key={wIdx} className="text-amber-800 leading-tight">
                          {w}
                        </p>
                      ))}
                    </div>
                  )}

                  {/* Sources & Citations Section */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
                      <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                        <FileText className="w-3 h-3 text-bis-blue" />
                        <span>Sources & Official Citations ({msg.sources.length})</span>
                      </p>
                      <div className="space-y-1.5">
                        {msg.sources.map((src, sIdx) => (
                          <div
                            key={sIdx}
                            className="bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg p-2 text-[11px] transition-colors flex items-start justify-between gap-2"
                          >
                            <div className="space-y-0.5 min-w-0">
                              <div className="font-medium text-slate-800 truncate">
                                {src.title || "BIS Reference Document"}
                              </div>
                              {src.url ? (
                                <a
                                  href={src.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-bis-blue hover:underline flex items-center space-x-1 text-[10px] truncate"
                                >
                                  <span className="truncate">{src.url}</span>
                                  <ExternalLink className="w-2.5 h-2.5 shrink-0" />
                                </a>
                              ) : (
                                <span className="text-slate-400 text-[10px]">Official Record</span>
                              )}
                            </div>
                            {src.source_type && (
                              <span className="shrink-0 text-[9px] font-semibold uppercase px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-200">
                                {src.source_type.replace(/_/g, " ")}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Interactive Clarification Options */}
                  {msg.clarification_needed && msg.clarification_options && msg.clarification_options.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
                      <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1">
                        <HelpCircle className="w-3 h-3 text-bis-blue" />
                        <span>Select a product category option:</span>
                      </p>
                      <div className="flex flex-col gap-1.5">
                        {msg.clarification_options.map((opt, oIdx) => (
                          <button
                            key={oIdx}
                            onClick={() => handleSendMessage(opt)}
                            className="text-left text-[11px] px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200 transition-all font-medium"
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Latency & Feedback Footer */}
                  {msg.sender === "assistant" && (
                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between text-[10px] text-slate-400 gap-2">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>
                          {msg.processing_time_ms ? `${msg.processing_time_ms}ms` : "Sahayak AI"}
                        </span>
                      </span>

                      {msg.id !== "welcome-1" && (
                        <div className="flex items-center space-x-1.5 bg-slate-50 px-2 py-0.5 rounded border border-slate-200 text-slate-500">
                          <button
                            onClick={() => handleCopyMessage(msg.id, msg.content)}
                            className={`p-0.5 rounded hover:text-bis-blue transition-colors flex items-center space-x-1 ${copiedId === msg.id ? "text-emerald-600 font-bold" : "text-slate-400"}`}
                            title="Copy response"
                          >
                            {copiedId === msg.id ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-600" />
                                <span className="text-[9px] text-emerald-600">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span className="text-[9px]">Copy</span>
                              </>
                            )}
                          </button>
                          <span className="text-slate-300">|</span>
                          <span className="text-[9px]">Helpful?</span>
                          <button
                            onClick={() => handleFeedback(msg.id, messages[messages.indexOf(msg) - 1]?.content || "", msg.content, true)}
                            className={`p-0.5 rounded hover:text-emerald-600 transition-colors ${feedbackMap[msg.id] === "positive" ? "text-emerald-600 font-bold" : "text-slate-400"}`}
                            title="Helpful response"
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => handleFeedback(msg.id, messages[messages.indexOf(msg) - 1]?.content || "", msg.content, false)}
                            className={`p-0.5 rounded hover:text-red-600 transition-colors ${feedbackMap[msg.id] === "negative" ? "text-red-600 font-bold" : "text-slate-400"}`}
                            title="Not helpful"
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>
                        </div>
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
                  <span className="font-medium text-slate-700">{loadingMessages[loadingStep]}</span>
                </div>
              </div>
            )}

            {/* Error Message */}
            {errorMessage && (
              <div className="bg-red-50 border border-red-200 text-red-800 p-3 rounded-xl text-xs flex items-start justify-between">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold">Request Notice</p>
                    <p className="text-[11px] text-red-700 mt-0.5">{errorMessage}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleSendMessage()}
                  className="bg-red-100 hover:bg-red-200 text-red-800 font-medium px-2 py-1 rounded text-[11px] transition-all"
                >
                  Retry
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
              e-BIS Sahayak AI Assistant provides general guidance. Always verify official notifications on bis.gov.in.
            </p>
          </div>
        </div>

        {/* Right Drawer: Sahayak AI Capabilities & Guidance */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 flex flex-col h-[650px] overflow-y-auto space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div className="flex items-center space-x-2">
              <Bot className="w-4 h-4 text-bis-blue" />
              <h2 className="text-sm font-bold text-slate-900">
                Sahayak AI Capabilities
              </h2>
            </div>
            <span className="text-[10px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-mono font-semibold">
              Groq AI
            </span>
          </div>

          <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-2">
              <h3 className="font-semibold text-slate-900 flex items-center space-x-1.5">
                <BookOpen className="w-4 h-4 text-bis-blue" />
                <span>What I Can Help With</span>
              </h3>
              <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-700">
                <li>Indian Standards (IS) general specifications</li>
                <li>Product-to-Standard applicability guidance</li>
                <li>ISI Mark (Scheme-I), CRS (Scheme-II), and FMCS concepts</li>
                <li>Quality Control Orders (QCO) information</li>
                <li>BIS testing laboratory discovery</li>
              </ul>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 space-y-2">
              <h3 className="font-semibold text-amber-900 flex items-center space-x-1.5">
                <ShieldCheck className="w-4 h-4 text-amber-600" />
                <span>Regulatory Guidance Notice</span>
              </h3>
              <p className="text-[11px] text-amber-800 leading-relaxed">
                e-BIS Sahayak provides general guidance based on official BIS principles. Specific mandatory compliance requirements, QCO dates, and fee schedules must always be verified on the official BIS portal (bis.gov.in).
              </p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-[11px] text-blue-900 space-y-1 mt-auto">
            <div className="flex items-center space-x-1 font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Multilingual Assistance</span>
            </div>
            <p className="text-blue-700 leading-relaxed text-[10px]">
              Available natively in English, Hindi (हिंदी), and Tamil (தமிழ்). Select your language in the top bar.
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
