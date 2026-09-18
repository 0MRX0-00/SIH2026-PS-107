# SIH 2026 Demonstration Scenarios (SIH26107)

## 1. Overview
This document outlines five verified, end-to-end demonstration scenarios for **e-BIS Sahayak**. Each scenario is designed to showcase the system's core capabilities to Smart India Hackathon evaluators and BIS officials.

---

## Scenario 1: Natural Language Product Discovery & Ambiguity Handling
* **Objective:** Demonstrate how a manufacturer with no prior standard knowledge discovers applicable Indian Standards (IS) and mandatory Quality Control Orders (QCOs).
* **Step 1 (Ambiguous Input):**
  - **User Query:** `"I manufacture bottles"`
  - **System Action:** Detects broad product scope. Triggers localized clarification questions (Material: Plastic/PET vs Glass vs Stainless Steel, Application: Packaged drinking water vs Infant feeding).
* **Step 2 (Clarified Input):**
  - **User Query:** `"I manufacture 3-Pin electrical domestic plugs and sockets"`
  - **System Action:** Returns **IS 1293:2019** (*Plugs and Socket-Outlets up to 250V and 16A*), highlights **Mandatory QCO status**, identifies applicable scheme (**Scheme-I ISI Mark**), and provides direct citation to *Clause 1.1 (Scope)*.

---

## Scenario 2: Source-Grounded Document Q&A with Verifiable Citations
* **Objective:** Demonstrate zero-hallucination conversational RAG with clause and page traceability.
* **User Query:** `"What are the rated voltages and currents specified in IS 1293:2019 Clause 6?"`
* **Workflow:**
  1. Vector similarity search retrieves `[EVIDENCE 1]` from `is_1293_plugs_sample.md` (Section 6, Clause 6.1 & 6.2).
  2. Groq LPU synthesizes a grounded technical response:
     - Standard rated voltage: **250 V a.c.**
     - Standard rated currents: **6 A, 16 A, and 25 A**
     - Table 1 configurations: Type D (6A 2-pin with earth), Type M (16A 3-pin with earth).
  3. Grounded Citation Inspector displays verified clause number (`Clause 6.1`), page number (`Page 2`), and SHA-256 verified source pass-through.

---

## Scenario 3: 5-Stage Certification Roadmap Wizard
* **Objective:** Guide an MSME through the exact compliance pathway for obtaining an ISI Mark license.
* **User Action:** Navigate to `/certification` and enter `"IS 1293:2019 Plugs"`.
* **System Output:**
  - **Stage 1 (Standard & QCO Verification):** Verifies mandatory QCO compliance requirement.
  - **Stage 2 (In-House Laboratory Setup):** Generates mandatory testing apparatus checklist (High voltage breakdown tester, insulation resistance meter, creepage caliper).
  - **Stage 3 (Manakonline Application):** Checklist of documents (Form V, factory layout, machinery invoices, brand authorization).
  - **Stage 4 (Factory Inspection & Sample Drawing):** BIS technical audit verification parameters.
  - **Stage 5 (License Grant & ISI Marking):** CML issuance, annual marking fees, and surveillance terms.

---

## Scenario 4: Multi-Criteria Testing Laboratory Finder
* **Objective:** Locate accredited laboratories authorized to conduct standard compliance testing.
* **User Action:** Navigate to `/laboratories`, select State: `"Tamil Nadu"`, Standard: `"IS 1293"`.
* **System Output:**
  - Identifies **BIS Southern Regional Laboratory (Chennai)** and **NABL-Accredited Electrical Testing House (Coimbatore)**.
  - Displays testing scope: *Insulation Resistance, Temperature Rise, Mechanical Strength, Shutter Reliability*.
  - Provides direct contact details, address, and accreditation validity.

---

## Scenario 5: Multilingual Interaction (हिन्दी & தமிழ்)
* **Objective:** Demonstrate native language interaction for grassroots entrepreneurs while preserving technical standard integrity.
* **Tamil Flow:**
  - **Query:** `"தமிழ்நாட்டில் பிளக் மற்றும் சாக்கெட்டுகளுக்கான BIS ஆய்வகங்கள் எவை?"`
  - **Answer:** Localized response in Tamil identifying the Chennai regional laboratory, with exact standard `IS 1293:2019` preserved without corrupted translation.
* **Hindi Flow:**
  - **Query:** `"IS 1293 क्लॉज 13.1 के तहत इंसुलेशन प्रतिरोध (Insulation Resistance) की क्या आवश्यकता है?"`
  - **Answer:** Synthesizes answer in Hindi specifying `5 MΩ` at `500V d.c.` with bracket citation `[1]`.
