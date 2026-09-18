# RAG Evaluation & Ground Truth Validation: e-BIS Sahayak

## 1. Evaluation Methodology
e-BIS Sahayak uses an empirical, automated evaluation framework (`app.evaluation.run`) running against a curated test dataset (`data/evaluation/evaluation_dataset.json`).

The evaluation measures:
1. **Retrieval Quality (Hit@K & MRR):** Whether the authoritative Indian Standard appears in the top retrieved chunks.
2. **Evidence Grounding Rate:** Percentage of factual technical claims backed by verified BIS source chunks.
3. **Citation Integrity:** Ratio of citations with verified clause and standard mappings.
4. **Hallucination Resistance:** Ability to correctly flag fictional standards, products, or non-existent clauses as `insufficient_evidence: true`.
5. **Multilingual Consistency:** Retrieval accuracy and terminology preservation across English, Hindi, and Tamil queries.
6. **Adversarial Robustness:** Defense against prompt injection and jailbreak payloads.

---

## 2. Empirical Benchmark Results

> **Evaluation Run Configuration:**
> - **Total Test Cases:** 25
> - **Test Suite File:** `data/evaluation/evaluation_dataset.json`
> - **Date of Execution:** September 2026

### 2.1 Retrieval Quality Metrics

| Metric | Measured Value | Definition |
|---|---|---|
| **Hit@1** | **81.2%** | Fraction of queries where the exact target standard was ranked #1 |
| **Hit@3** | **93.8%** | Fraction of queries where the target standard appeared in top 3 |
| **Hit@5** | **93.8%** | Fraction of queries where the target standard appeared in top 5 |
| **Mean Reciprocal Rank (MRR)** | **0.8646** | $\frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$ |
| **Average Retrieval Latency** | **28.13 ms** | Dense FastEmbed embedding + cosine similarity search |

---

### 2.2 Grounding & Citation Integrity

| Metric | Measured Value | Definition |
|---|---|---|
| **Evidence Grounding Rate** | **100.0%** | Factual responses containing verified source citations |
| **Total Citations Checked** | **76 citations** | Inspected across test corpus |
| **Valid Citation Rate** | **65.8%** | Citations linking directly to exact standard + clause |
| **Invalid Citation Rate** | **34.2%** | Citations requiring broader document-level fallback |

---

### 2.3 Safety & Hallucination Resistance

| Test Category | Resistance / Defense Rate | Target Behavior |
|---|---|---|
| **Fictional Standard Queries (No Evidence)** | **100.0%** | Returns `insufficient_evidence: true` without fabrication |
| **Fictional Product Queries** | **100.0%** | Rejects unsupported products (e.g. quantum devices) |
| **Adversarial / Prompt Injections** | **100.0%** | Resists jailbreaks and maintains grounding invariant |

---

### 2.4 Multilingual Distribution

| Language | Test Cases | Retrieval Hits | Grounded Responses |
|---|---|---|---|
| **English (`en`)** | 14 | 10 | 11 |
| **Hindi (`hi`)** | 6 | 3 | 4 |
| **Tamil (`ta`)** | 5 | 2 | 4 |

---

## 3. Running Evaluation Locally
To reproduce the empirical evaluation benchmarks:
```bash
cd backend
python -m app.evaluation.run
```
The full JSON report is output to `data/evaluation/evaluation_report.json`.
