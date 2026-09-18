# Problem Statement: e-BIS Sahayak

**SIH 2026 Problem Statement ID:** SIH26107  
**Project Title:** e-BIS Sahayak (AI-Powered Intelligent Assistant for Indian Standards & BIS Services)  
**Target Beneficiaries:** Micro, Small & Medium Enterprises (MSMEs), Startups, Manufacturers, Industry Bodies, Conformity Assessment Bodies & Testing Labs, Consumers, and BIS Officials.

---

## 1. Background & Context

The Bureau of Indian Standards (BIS) is the National Standard Body of India established under the BIS Act 2016. BIS is responsible for the harmonious development of activities of standardization, marking, and quality certification of goods.

Currently, BIS oversees:
* Over **21,000+ Indian Standards (IS)** spanning 15 broad technical divisions (Civil, Mechanical, Electrotechnical, Food & Agriculture, Textiles, Chemical, Electronics & IT, etc.).
* Multiple certification schemes: **ISI Mark** (Product Certification Scheme I), **Compulsory Registration Scheme (CRS)** for electronic goods, **Foreign Manufacturers Certification Scheme (FMCS)**, **Hallmarking** for gold and silver, and **Management Systems Certification (MSCS)**.
* A nationwide network of recognized testing laboratories, conformity assessment procedures, and Quality Control Orders (QCOs) issued by various Ministries making standards mandatory.

---

## 2. Key Challenges & Pain Points

1. **Information Fragmentation & Complexity:**  
   Navigating thousands of dense PDF standards, amendments, Quality Control Orders (QCOs), and product manuals is overwhelming for MSMEs, startups, and new entrepreneurs who lack dedicated regulatory compliance teams.

2. **Standard Identification Gap:**  
   Manufacturers often struggle to determine the exact Indian Standard applicable to their specific product category, composition, or intended usage.

3. **Complex Conformity & Certification Pathways:**  
   Understanding whether a standard falls under mandatory QCO compliance vs. voluntary certification, the specific testing parameters required, sample sizes, and step-by-step application procedures is difficult.

4. **Testing Laboratory Discovery:**  
   Identifying which BIS-recognized or NABL-accredited laboratories are authorized to perform specific test clauses for a given standard is non-trivial.

5. **Lack of Grounded, Traceable AI Guidance:**  
   Generic conversational AI systems frequently hallucinate regulatory clauses, generate outdated standard numbers, or fabricate compliance steps, which can lead to severe legal and financial repercussions for manufacturers.

---

## 3. Project Objective: e-BIS Sahayak

`e-BIS Sahayak` is an intelligent, bilingual/multilingual conversational assistant and discovery platform designed to provide:
* **Grounded, Source-Backed Guidance:** Every answer is backed by precise citations referencing the exact Indian Standard (IS number), year of publication, clause/sub-clause, page number, and document identifier.
* **Product-to-Standard Mapping:** Intuitive matching of manufacturer product specs to relevant IS codes and QCO mandates.
* **Certification & Compliance Navigator:** Step-by-step roadmap for obtaining ISI mark, CRS registration, Hallmarking, or Lab recognition.
* **Transparent Citations & Fact Verifiability:** Side-by-side evidence inspection so users can verify guidance directly against official gazettes and standards.

---

## 4. Phase 1 Scope & Boundary

In **Phase 1 (Foundation)**:
* We construct the complete production-grade architecture, database schema, API routing, frontend shell, containerization, and technical documentation.
* We establish strict boundaries: no mock or hallucinated BIS information is served; placeholders clearly indicate upcoming capabilities.
* The system is structured to seamlessly plug in the RAG pipeline, Groq LLM inference, embedding generation, and Qdrant vector retrieval in subsequent phases.
