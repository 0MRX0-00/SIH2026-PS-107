# Multilingual AI Architecture & Cross-Lingual RAG

## 1. Overview
e-BIS Sahayak (SIH 2026 Problem Statement SIH26107) supports multilingual intelligence across **English (`en`)**, **Hindi (`hi` - हिन्दी)**, and **Tamil (`ta` - தமிழ்)**.

The system ensures that users across India—ranging from small-scale rural manufacturers and artisans to state industrial promotion officers and consumers—can interact seamlessly in their preferred language while receiving **authoritative, 100% source-grounded answers** cited from Indian Standards (IS).

```
   ┌─────────────────────────────────────────────────────────────┐
   │                  User Multilingual Query                    │
   │           (English / हिन्दी Devanagari / தமிழ் Tamil)        │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │            Language Detection & Disambiguation              │
   │  - Unicode Script Classifier (Latin, Devanagari, Tamil)      │
   │  - Manual Session Override (EN / HI / TA)                   │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │           Cross-Lingual Domain Query Translation            │
   │  - Maps regional product/technical terms to English terms   │
   │  - Preserves exact standard numbers (e.g., IS 1293:2019)    │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │           Dense Vector Retrieval in Qdrant                  │
   │  - FastEmbed BAAI/bge-small-en-v1.5                         │
   │  - Fast & accurate retrieval against English BIS repository │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │          Groq Multilingual Grounded Synthesis               │
   │  - Llama-3.3-70b-versatile via Groq LPU                     │
   │  - Strict Terminology Preservation Rules                    │
   │  - Zero-Hallucination Guardrails & Verbatim Citations       │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                 Multilingual UI & Insights                  │
   │  - React LanguageContext + Structured Locale Dictionaries    │
   │  - Native Script Rendering & Localized Suggestions          │
   └─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 Language Detection Service (`LanguageService`)
- **Deterministic Unicode Script Analysis**: Classifies input text by analyzing script codepoint ranges:
  - Devanagari (`\u0900-\u097F`) ➔ `hi`
  - Tamil (`\u0B80-\u0BFF`) ➔ `ta`
  - Latin (`\u0020-\u007F`) ➔ `en`
- **Fallback & Manual Override**: Session preferences take precedence when explicitly selected by the user.

### 2.2 Cross-Lingual Vector Retrieval
- Authoritative Indian Standards documents are indexed in English.
- The `LanguageService` translates domain-specific keywords from Hindi/Tamil into English search queries (e.g., "प्रेशर कुकर" ➔ "pressure cooker", "மின்விசிறி" ➔ "ceiling fan").
- The enriched query performs dense embedding and cosine similarity search in **Qdrant Vector DB**, retrieving relevant clauses and tables without modifying document metadata.

### 2.3 Strict Terminology Preservation Rules
When synthesizing responses in Hindi or Tamil, the Groq LPU model follows strict preservation constraints:
1. **Standard Numbers:** Must NEVER be translated or altered (`IS 1293:2019`, `IS/ISO 9001`, etc.).
2. **Clause References:** Must preserve exact numbers (`Clause 13.1`, `खंड 13.1`, `பிரிவு 13.1`).
3. **Bracket Citations:** Bracket citations (`[1]`, `[2]`) must link directly to the source evidence items.
4. **Units of Measurement:** Preserve SI units (`mm`, `V`, `A`, `Hz`, `MΩ`, `kV`).

### 2.4 Multilingual Product Discovery & Ambiguity Handling
- Ambiguous product descriptions in Hindi or Tamil are identified dynamically.
- The assistant generates localized clarification questions in the user's native language to narrow down the exact BIS standard and applicable Quality Control Order (QCO).

---

## 3. Supported Languages Matrix

| Language Code | Language Name | Native Script | Unicode Range | UI Localization | RAG Retrieval | Product Discovery |
|---|---|---|---|---|---|---|
| `en` | English | Latin | `\u0020-\u007F` | ✅ Complete | ✅ Native | ✅ Complete |
| `hi` | Hindi | Devanagari (हिन्दी) | `\u0900-\u097F` | ✅ Complete | ✅ Cross-Lingual | ✅ Complete |
| `ta` | Tamil | Tamil (தமிழ்) | `\u0B80-\u0BFF` | ✅ Complete | ✅ Cross-Lingual | ✅ Complete |

---

## 4. Frontend Internationalization (i18n)

- **Locale Dictionaries:** `frontend/src/locales/en.json`, `hi.json`, `ta.json`.
- **LanguageContext:** Provides `language`, `setLanguage`, and `t(key)` helper with fallback to English.
- **Client State Persistence:** Persists selected language in `localStorage` across all pages (`/`, `/assistant`, `/standards`, `/certification`, `/laboratories`).
