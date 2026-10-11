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
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  AlertCircle,
  Clock,
  BookOpen,
  ExternalLink,
  Plus,
  ArrowRight,
  Layers,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  sendChatMessage,
  ChatMessageInput,
  ChatResponse,
  submitFeedback,
  SourceItem,
} from "@/lib/api";
import { useLanguage } from "@/context/LanguageContext";
import { saveRecentConsultation } from "@/lib/consultations";

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
    "What is IS 1293:2019 and what are the socket safety requirements?",
    "Which Indian Standard applies to stainless steel water bottles?",
    "What certificates do I need to start an electronics business?",
    "How does Scheme-II Compulsory Registration (CRS) work?",
    "Where can I test electric ceiling fans under IS 17803 in India?",
  ],
  hi: [
    "IS 1293:2019 क्या है और सॉकेट सुरक्षा आवश्यकताएं क्या हैं?",
    "स्टेनलेस स्टील पानी की बोतलों पर कौन सा भारतीय मानक लागू होता है?",
    "इलेक्ट्रॉनिक्स व्यवसाय शुरू करने के लिए कौन से प्रमाण पत्र आवश्यक हैं?",
    "योजना-II अनिवार्य पंजीकरण (CRS) कैसे काम करता है?",
    "भारत में IS 17803 के तहत सीलिंग पंखे का परीक्षण कहाँ करवा सकते हैं?",
  ],
  ta: [
    "IS 1293:2019 என்றால் என்ன மற்றும் சாக்கெட் பாதுகாப்பு தேவைகள் என்ன?",
    "துருப்பிடிக்காத எஃகு தண்ணீர் பாட்டில்களுக்கு எந்த இந்திய தரநிலை பொருந்தும்?",
    "எலக்ட்ரானிக்ஸ் தொழிலைத் தொடங்க என்ன சான்றிதழ்கள் தேவை?",
    "திட்டம்-II கட்டாய பதிவு (CRS) எவ்வாறு செயல்படுகிறது?",
    "இந்தியாவில் IS 17803 இன் கீழ் மின் விசிறிகளை எங்கு சோதிக்கலாம்?",
  ],
};

function AssistantContent() {
  const { language, t } = useLanguage();
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialPrompt = searchParams.get("prompt") || "";
  const isNew = searchParams.get("new") === "true";

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome-1",
      sender: "assistant",
      content: t(
        "assistant.welcome_message",
        "Hello! I am e-BIS Sahayak, your official guide for Indian Standards (IS), mandatory Quality Control Orders (QCOs), certification schemes (ISI Mark, CRS, FMCS), and accredited laboratory testing facilities. How can I assist your compliance requirements today?"
      ),
      created_at: new Date(),
    },
  ]);

  const [inputQuery, setInputQuery] = useState(initialPrompt);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastFailedQuery, setLastFailedQuery] = useState<string | null>(null);
  const [feedbackMap, setFeedbackMap] = useState<Record<string, "positive" | "negative">>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Reset conversation if ?new=true
  useEffect(() => {
    if (isNew) {
      setMessages([
        {
          id: `welcome-${Date.now()}`,
          sender: "assistant",
          content: t(
            "assistant.welcome_message",
            "Hello! I am e-BIS Sahayak, your official guide for Indian Standards (IS), mandatory Quality Control Orders (QCOs), certification schemes (ISI Mark, CRS, FMCS), and accredited laboratory testing facilities. How can I assist your compliance requirements today?"
          ),
          created_at: new Date(),
        },
      ]);
      setInputQuery("");
      setErrorMessage(null);
      // Clean query params
      router.replace("/assistant");
    }
  }, [isNew, router, t]);

  // Handle initial prompt from navigation
  useEffect(() => {
    if (initialPrompt && !isNew) {
      handleSendMessage(initialPrompt);
      // Clean query params
      router.replace("/assistant");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialPrompt]);

  // Loading steps animation
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < 2 ? prev + 1 : prev));
      }, 1400);
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleCopyMessage = (msgId: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleFeedback = async (
    msgId: string,
    query: string,
    answer: string,
    isHelpful: boolean
  ) => {
    setFeedbackMap((prev) => ({
      ...prev,
      [msgId]: isHelpful ? "positive" : "negative",
    }));
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

  const handleResetConversation = () => {
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        sender: "assistant",
        content: t(
          "assistant.welcome_message",
          "Hello! I am e-BIS Sahayak, your official guide for Indian Standards (IS), mandatory Quality Control Orders (QCOs), certification schemes (ISI Mark, CRS, FMCS), and accredited laboratory testing facilities. How can I assist your compliance requirements today?"
        ),
        created_at: new Date(),
      },
    ]);
    setInputQuery("");
    setErrorMessage(null);
  };

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend !== undefined ? textToSend : inputQuery).trim();
    if (!query || isLoading) return;

    if (textToSend === undefined) {
      setInputQuery("");
    }
    setErrorMessage(null);
    setLastFailedQuery(null);

    // Save into real recent consultations
    saveRecentConsultation(query);

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
        .filter((m) => !m.id.startsWith("welcome-"))
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
      console.error("Chat API error:", err);
      const friendlyError =
        err.message ||
        "An unexpected error occurred while communicating with the server. Please try again.";
      setErrorMessage(friendlyError);
      setLastFailedQuery(query);
    } finally {
      setIsLoading(false);
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const currentSuggestions = SAMPLE_SUGGESTIONS[language] || SAMPLE_SUGGESTIONS.en;

  // Simple rich text formatter for assistant answers
  const renderFormattedContent = (content: string) => {
    const lines = content.split("\n");
    return (
      <div className="space-y-2.5 text-sm leading-relaxed text-[#0F172A]">
        {lines.map((line, idx) => {
          const trimmed = line.trim();
          if (!trimmed) {
            return <div key={idx} className="h-1.5" />;
          }

          // Header lines: ### or ##
          if (trimmed.startsWith("### ")) {
            return (
              <h4 key={idx} className="font-bold text-slate-900 text-sm mt-3 pt-1 border-b border-slate-100 pb-1">
                {trimmed.replace(/^###\s+/, "")}
              </h4>
            );
          }
          if (trimmed.startsWith("## ")) {
            return (
              <h3 key={idx} className="font-bold text-[#071324] text-base mt-4 mb-1">
                {trimmed.replace(/^##\s+/, "")}
              </h3>
            );
          }

          // Bullet points: * or -
          if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
            const bulletText = trimmed.replace(/^[\*\-]\s+/, "");
            return (
              <div key={idx} className="flex items-start space-x-2 pl-2">
                <span className="text-amber-500 font-bold text-xs mt-1 shrink-0">•</span>
                <span className="flex-1 text-slate-800">
                  {formatInlineText(bulletText)}
                </span>
              </div>
            );
          }

          // Numbered lists: 1. 2.
          const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
          if (numMatch) {
            return (
              <div key={idx} className="flex items-start space-x-2 pl-2">
                <span className="text-blue-900 font-bold text-xs mt-0.5 shrink-0 bg-blue-50 border border-blue-200 px-1 rounded-sm">
                  {numMatch[1]}
                </span>
                <span className="flex-1 text-slate-800">
                  {formatInlineText(numMatch[2])}
                </span>
              </div>
            );
          }

          // Default paragraph
          return (
            <p key={idx} className="text-slate-800">
              {formatInlineText(trimmed)}
            </p>
          );
        })}
      </div>
    );
  };

  // Format bold text **text** and inline codes `IS 1293`
  const formatInlineText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-bold text-slate-950">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code
            key={i}
            className="px-1.5 py-0.5 rounded-md bg-slate-100 text-blue-950 font-mono text-xs border border-slate-200"
          >
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  const loadingStepsText = [
    t("assistant.loading_step_1", "Parsing regulatory query and entity intents..."),
    t("assistant.loading_step_2", "Checking authentic BIS standards & QCO registry..."),
    t("assistant.loading_step_3", "Synthesizing source-grounded response via Groq LPU..."),
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] min-h-[550px] bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden">
      {/* Top Conversation Header */}
      <div className="bg-[#071324] text-white px-5 py-3.5 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center text-slate-950 shadow-xs">
            <Bot className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-bold text-sm text-white">
                {t("assistant.header_title", "e-BIS Sahayak AI Assistant")}
              </h2>
              <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950 border border-emerald-800 px-1.5 py-0.2 rounded-xs">
                Groq LPU Grounded
              </span>
            </div>
            <p className="text-[11px] text-slate-300">
              {t(
                "assistant.header_subtitle",
                "Official Indian Standards, QCOs, Schemes & Laboratory Guidance"
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleResetConversation}
            className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-xl border border-slate-700 transition-colors"
            title="Start new conversation"
          >
            <Plus className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">
              {t("assistant.new_chat_btn", "New Conversation")}
            </span>
          </button>
        </div>
      </div>

      {/* Messages Stream Container */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 bg-slate-50/60">
        {messages.map((msg, index) => {
          const isUser = msg.sender === "user";
          const queryText =
            isUser && index > 0
              ? msg.content
              : messages[index - 1]?.sender === "user"
              ? messages[index - 1]?.content
              : "";

          return (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${
                isUser ? "flex-row-reverse space-x-reverse" : "flex-row"
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-xs ${
                  isUser
                    ? "bg-[#152E4D] text-white"
                    : "bg-[#071324] text-amber-400 border border-slate-700"
                }`}
              >
                {isUser ? (
                  <User className="w-4 h-4" />
                ) : (
                  <ShieldCheck className="w-4 h-4 stroke-[2.5]" />
                )}
              </div>

              {/* Message Bubble Body */}
              <div
                className={`max-w-2xl sm:max-w-3xl rounded-2xl p-4 sm:p-5 shadow-xs transition-all ${
                  isUser
                    ? "bg-[#152E4D] text-white rounded-tr-xs"
                    : "bg-white border border-slate-200 text-slate-900 rounded-tl-xs"
                }`}
              >
                {/* User Message */}
                {isUser ? (
                  <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">
                    {msg.content}
                  </p>
                ) : (
                  /* Assistant Message */
                  <div className="space-y-4">
                    {/* Main Text Content */}
                    {renderFormattedContent(msg.content)}

                    {/* Clarification Choice Chips (if returned by backend) */}
                    {msg.clarification_options && msg.clarification_options.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-100">
                        <p className="text-xs font-bold text-slate-700 mb-2">
                          Select an option to clarify:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {msg.clarification_options.map((opt, optIdx) => (
                            <button
                              key={optIdx}
                              onClick={() => handleSendMessage(opt)}
                              className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200 px-3 py-1.5 rounded-xl font-medium transition-colors text-left flex items-center space-x-1.5"
                            >
                              <span>{opt}</span>
                              <ChevronRight className="w-3.5 h-3.5 text-blue-700" />
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Official Sources & Gazette References */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-4 pt-3.5 border-t border-slate-100">
                        <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-900 mb-2.5">
                          <BookOpen className="w-4 h-4 text-emerald-600" />
                          <span>Official Source Citations & Gazette References:</span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                          {msg.sources.map((src, sIdx) => (
                            <div
                              key={sIdx}
                              className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex flex-col justify-between hover:border-emerald-300 transition-colors"
                            >
                              <div className="space-y-1">
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100/70 border border-emerald-300 px-1.5 py-0.2 rounded-xs">
                                    {src.authority || "Official BIS Record"}
                                  </span>
                                  {src.verified && (
                                    <span className="text-[9px] font-bold text-slate-500">
                                      Verified
                                    </span>
                                  )}
                                </div>
                                <h5 className="font-semibold text-xs text-slate-900 line-clamp-2">
                                  {src.title || "Indian Standard Official Order"}
                                </h5>
                                {src.provenance && (
                                  <p className="text-[10px] text-slate-500 line-clamp-1">
                                    Provenance: {src.provenance}
                                  </p>
                                )}
                              </div>

                              {src.url && (
                                <a
                                  href={src.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="mt-2.5 inline-flex items-center space-x-1 text-[11px] font-bold text-blue-700 hover:text-blue-900"
                                >
                                  <span>View Official Reference</span>
                                  <ExternalLink className="w-3 h-3" />
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Footer Actions: Copy, Feedback, Time */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs text-slate-400">
                      <div className="flex items-center space-x-3">
                        {/* Copy Action */}
                        <button
                          onClick={() => handleCopyMessage(msg.id, msg.content)}
                          className="flex items-center space-x-1 hover:text-slate-700 transition-colors text-[11px]"
                          title="Copy response"
                        >
                          {copiedId === msg.id ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-600" />
                              <span className="text-emerald-600 font-semibold">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3.5 h-3.5" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>

                        {/* Thumbs Feedback */}
                        {!msg.id.startsWith("welcome-") && (
                          <div className="flex items-center space-x-1 pl-2 border-l border-slate-200">
                            <button
                              onClick={() =>
                                handleFeedback(msg.id, queryText, msg.content, true)
                              }
                              className={`p-1 rounded-sm transition-colors ${
                                feedbackMap[msg.id] === "positive"
                                  ? "text-emerald-600 bg-emerald-50"
                                  : "hover:text-slate-700"
                              }`}
                              title="Helpful response"
                            >
                              <ThumbsUp className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() =>
                                handleFeedback(msg.id, queryText, msg.content, false)
                              }
                              className={`p-1 rounded-sm transition-colors ${
                                feedbackMap[msg.id] === "negative"
                                  ? "text-rose-600 bg-rose-50"
                                  : "hover:text-slate-700"
                              }`}
                              title="Not helpful"
                            >
                              <ThumbsDown className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </div>

                      {/* Processing Timing */}
                      {msg.processing_time_ms && (
                        <div className="flex items-center space-x-1 text-[10px] text-slate-400">
                          <Clock className="w-3 h-3" />
                          <span>{msg.processing_time_ms} ms</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-xl bg-[#071324] text-amber-400 border border-slate-700 flex items-center justify-center shrink-0 shadow-xs">
              <ShieldCheck className="w-4 h-4 stroke-[2.5]" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 shadow-xs max-w-md space-y-2.5">
              <div className="flex items-center space-x-2">
                <RefreshCw className="w-4 h-4 text-amber-600 animate-spin" />
                <span className="text-xs font-bold text-slate-800">
                  {loadingStepsText[loadingStep] || "Processing consultation..."}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-1 overflow-hidden">
                <div
                  className="bg-amber-500 h-1 transition-all duration-700 ease-out"
                  style={{ width: `${(loadingStep + 1) * 33}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Error Notice & Retry */}
        {errorMessage && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-start space-x-3 text-rose-800 text-xs">
            <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
            <div className="flex-1 space-y-1">
              <p className="font-bold">Error Processing Query</p>
              <p>{errorMessage}</p>
              {lastFailedQuery && (
                <button
                  onClick={() => handleSendMessage(lastFailedQuery)}
                  className="mt-2 inline-flex items-center space-x-1 bg-rose-600 text-white font-bold px-3 py-1 rounded-lg text-[11px] hover:bg-rose-700 transition-colors"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Retry Query</span>
                </button>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions (shown when conversation is fresh) */}
      {messages.length <= 1 && (
        <div className="px-5 py-2.5 bg-slate-50 border-t border-slate-100">
          <p className="text-[11px] font-bold text-slate-500 mb-1.5">
            Suggested compliance queries:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {currentSuggestions.slice(0, 3).map((sugg, sIdx) => (
              <button
                key={sIdx}
                onClick={() => handleSendMessage(sugg)}
                className="text-xs bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-1 rounded-lg transition-colors truncate max-w-sm text-left"
              >
                {sugg}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Composer Bar */}
      <div className="p-4 bg-white border-t border-slate-200">
        <div className="relative flex items-end gap-2 bg-slate-50 border border-slate-300 rounded-2xl p-2 focus-within:ring-2 focus-within:ring-amber-500/50 focus-within:border-amber-500 focus-within:bg-white transition-all shadow-xs">
          <textarea
            ref={textareaRef}
            value={inputQuery}
            onChange={(e) => {
              setInputQuery(e.target.value);
              // Auto-expand textarea up to 160px
              e.target.style.height = "auto";
              e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
            }}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={t(
              "assistant.input_placeholder",
              "Ask standard, QCO, certification or testing question (Press Enter to send)..."
            )}
            rows={1}
            className="flex-1 text-sm bg-transparent border-0 resize-none text-slate-900 placeholder-slate-400 focus:outline-hidden p-1.5 min-h-[38px] max-h-[160px]"
            aria-label="Message Input"
          />

          <button
            onClick={() => handleSendMessage()}
            disabled={!inputQuery.trim() || isLoading}
            className={`p-2.5 rounded-xl font-bold transition-all shrink-0 ${
              inputQuery.trim() && !isLoading
                ? "bg-amber-500 text-slate-950 hover:bg-amber-400 shadow-sm active:scale-95"
                : "bg-slate-200 text-slate-400 cursor-not-allowed"
            }`}
            aria-label="Send Message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center justify-between mt-2 px-1 text-[11px] text-slate-400">
          <span>Enter to send • Shift+Enter for new line</span>
          <span className="text-slate-500">
            Powered by Groq Cloud LPU • Deterministic Catalog Grounding
          </span>
        </div>
      </div>
    </div>
  );
}

export default function AssistantPage() {
  return (
    <Suspense
      fallback={
        <div className="p-12 text-center text-slate-500">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-amber-500" />
          <p className="text-sm font-semibold">Loading e-BIS Sahayak Assistant...</p>
        </div>
      }
    >
      <AssistantContent />
    </Suspense>
  );
}
