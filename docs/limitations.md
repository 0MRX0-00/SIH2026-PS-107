# e-BIS Sahayak — System Limitations & Boundaries
**Smart India Hackathon 2026 • Problem Statement SIH26107**  
*AI-Powered Intelligent Assistant for Indian Standards & BIS Services*

---

## 1. Scope & System Boundaries

e-BIS Sahayak is an AI assistant developed for informational and compliance assistance. To ensure safety and regulatory fidelity, the system operates under the following known boundaries:

1. **Non-Legal Advisory Disclaimer**:
   - The information provided by e-BIS Sahayak is for guidance and does not replace official Gazette notifications or formal regulatory determinations issued by the Bureau of Indian Standards (BIS) or relevant line ministries (e.g. DPIIT, MeitY).
2. **Current Document Corpus**:
   - The current knowledge base indexes 5 core standard categories (`IS 1293:2019`, `IS 2347:2017`, `IS 1061:2017`, `IS 694:2010`, `IS 15885 (Part 2/Sec 13):2012`), major QCO notifications, certification scheme manuals (ISI, CRS, FMCS), and accredited laboratory directories.
   - For standards outside this indexed corpus, the system operates in strict grounded fallback mode rather than generating unverified content.
3. **Multilingual Script Support**:
   - Native support is verified for **English**, **हिन्दी (Hindi)**, and **தமிழ் (Tamil)**. Other Indic languages (Telugu, Bengali, Marathi, Gujarati) will be expanded in the next phase.
4. **Offline Mode**:
   - Embedding generation and vector search run entirely locally/on-premise; high-level LLM synthesis utilizes Groq cloud inference API requiring outbound internet access (or local Ollama/vLLM backend in fully air-gapped environments).
