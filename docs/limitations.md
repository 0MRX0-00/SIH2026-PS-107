# e-BIS Sahayak — System Limitations & Boundaries
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

## 1. Scope & System Boundaries

e-BIS Sahayak is an AI assistant developed for informational and compliance assistance. To ensure safety and regulatory fidelity, the system operates under the following known boundaries:

1. **Non-Legal Advisory Disclaimer**:
   - The information provided by e-BIS Sahayak is for guidance and does not replace official Gazette notifications or formal regulatory determinations issued by the Bureau of Indian Standards (BIS) or relevant line ministries (e.g., DPIIT, MeitY, Ministry of Power).

2. **Curated Seed Data Knowledge Base**:
   - The current knowledge base operates on a curated seed catalog of verified standards (`app/db/seed_intelligence.py`) rather than a full semantic vector database over 21,000+ Indian Standards.
   - Core standards explicitly indexed include:
     - **IS 1293:2019** (Plugs and Socket-Outlets up to 16 A)
     - **IS 13252 (Part 1):2010** (Information Technology Equipment Safety / CRS)
     - **IS 17803:2022** (Electric Ceiling Type Fans / BLDC)
     - **IS 14543:2016** (Packaged Drinking Water)
     - **IS 17526:2021** (Stainless Steel Water Bottles & Vacuum Flasks)
     - **IS 6911:2017** (Food-Grade Stainless Steel Materials)
     - **IS 7372:2021** (Automotive Lead-Acid Storage Batteries)
   - It also covers major QCO notifications, certification scheme frameworks (Scheme-I ISI, Scheme-II CRS, Scheme-IV FMCS), and accredited laboratory directories.

3. **Scaling to Additional Standards**:
   - For queries outside this curated seed catalog, the system operates in strict grounded abstention mode (`insufficient_evidence=True`), declining to answer rather than hallucinating standard numbers or clause contents.
   - Scaling to cover all 21,000+ Indian Standards requires either expanding the curated seed catalog registry or integrating a full production vector database retrieval engine.

4. **Multilingual Script Support**:
   - Native support is verified for **English**, **हिन्दी (Hindi)**, **Hinglish (Romanized Hindi)**, and **தமிழ் (Tamil)**.

5. **LLM Inference Dependency**:
   - Intent routing, keyword matching, and data lookup run deterministically in Python; final evidence-constrained response formatting utilizes Groq cloud inference API (`llama-3.3-70b-versatile`).
