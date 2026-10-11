# e-BIS Sahayak — SIH 2026 Live Demonstration Script
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

## 🕒 Demonstration Timeline (8-10 Minutes Total)

### Act 1: Problem Introduction & National Impact (1.5 Minutes)
- **Presenter 1:** "Good morning, respected judges. Indian businesses, startups, and MSMEs lose millions of work hours struggling through dense 80-page BIS technical standards, scattered QCO notifications across ministry gazettes, and unclear certification pathways."
- **Presenter 1:** "Our solution, **e-BIS Sahayak**, bridges this gap through a high-precision, multilingual, source-grounded intelligence system powered by Groq LPU with deterministic catalog lookup and official gazette evidence verification."

---

### Act 2: Conversational Assistant & Grounded Evidence Demo (2.5 Minutes)
1. **Scenario 1: Mandatory QCO applicability**
   - **Query:** *"Is ISI mark mandatory for plugs and socket-outlets, and which standard applies?"*
   - **Showcase:** 
     - Sahayak identifies `IS 1293:2019` with relevant technical clauses and testing scope.
     - Highlights mandatory Quality Control Order (QCO) issued by DPIIT.
     - Displays clickable official source citation cards with verified portal links and data provenance.
2. **Scenario 2: Strict Evidence Defense**
   - **Query:** *"What is the standard test procedure for warp-speed starship engine shielding?"*
   - **Showcase:** 
     - Sahayak detects that no verified BIS standard matches this fictional query.
     - Returns clear evidence-based abstention stating no verified BIS standard exists, refusing to invent fictitious requirements.
3. **Scenario 3: Direct Clause Deep-Dive**
   - **Query:** *"What are the mandatory marking requirements under IS 2347 for domestic pressure cookers?"*
   - **Showcase:**
     - Sahayak identifies `Clause 10` markings: Nominal capacity, Manufacturer name/trademark, and mandatory ISI certification mark.

---

### Act 3: Multilingual Seamless Interaction (1.5 Minutes)
1. **Switch UI language to हिन्दी (Hindi):**
   - **Query:** *"प्रेशर कुकर के लिए कौन सा बीआईएस मानक लागू होता है और क्या यह अनिवार्य है?"*
   - **Showcase:**
     - Natural Hindi language interaction citing `IS 2347:2017` with official gazette reference.
2. **Switch UI language to தமிழ் (Tamil):**
   - **Query:** *"பிளக் மற்றும் சாக்கெட்டுகளுக்கான ஐஎஸ்ஐ மார்க் கட்டாயமா?"*
   - **Showcase:**
     - Fluent Tamil response citing `IS 1293:2019` with official BIS citations.

---

### Act 4: Certification Navigator & Accredited Lab Finder (2 Minutes)
1. **Certification Roadmap Wizard (`/certification`):**
   - Enter *"Plugs and Socket-Outlets"*.
   - Walk through the guided roadmap:
     - *Step 1: Standard Identification (`IS 1293:2019`)*
     - *Step 2: Factory Testing Facilities setup*
     - *Step 3: Manakonline Portal Application submission*
     - *Step 4: Factory Inspection by BIS auditor*
     - *Step 5: Grant of ISI Mark License & CML Number*
2. **Accredited Laboratory Directory (`/laboratories`):**
   - Search by standard `IS 1293`.
   - Filter by State (e.g. *Delhi* or *Haryana*).
   - Display verified laboratories from the 576-laboratory LIMS directory with contact information and accreditation scope.

---

### Act 5: Operations, Security Controls & Admin Management (1.5 Minutes)
1. **Admin Console (`/admin`):**
   - Enter your configured Admin Key (e.g. `<your-admin-secret-key>`).
   - Inspect verified catalog records, source provenance, and laboratory registry status.
   - Show live user feedback metrics (helpful ratings and issue categories).
2. **Reliability & Security Controls:**
   - **Pure ASGI Size Limiter:** Enforces strict 2 MB payload limits across declared and chunked streaming requests (HTTP 413).
   - **Bounded Rate Limiter:** 10,000-entry capacity with LRU eviction to prevent memory exhaustion under IP churn.
   - **Protected Debug Observability:** `/api/v1/chat/debug` guarded behind administrator authentication.
   - **100% Deterministic Test Suite:** 283 passed / 283 tests in under 4 seconds with zero external network dependencies.

---

### Act 6: Summary & Judge Q&A (1 Minute)
- **Presenter 2:** "e-BIS Sahayak is production-ready, fully verified with 283 passing automated tests, supports Indian manufacturing across 3 languages, and stands ready to empower Make in India compliance."
