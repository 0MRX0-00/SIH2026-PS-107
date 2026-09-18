import asyncio
import json
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.evaluation.evaluator import RAGEvaluator


async def main():
    print("=" * 70)
    print("e-BIS Sahayak — Automated RAG & Grounding Evaluation Runner")
    print("=" * 70)

    evaluator = RAGEvaluator()
    print(f"Loading test dataset from: {evaluator.dataset_path}")

    try:
        report = await evaluator.evaluate_all()
    except Exception as e:
        print(f"Evaluation failed with error: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY & EMPIRICAL METRICS")
    print("=" * 70)

    print(f"Total Test Cases Evaluated : {report['summary']['total_test_cases']}")
    print(f"Execution Duration         : {report['summary']['evaluation_duration_seconds']}s")

    print("\n[Retrieval Quality Metrics]")
    print(f"  Hit@1 Rate               : {report['retrieval_metrics']['hit_at_1']}%")
    print(f"  Hit@3 Rate               : {report['retrieval_metrics']['hit_at_3']}%")
    print(f"  Hit@5 Rate               : {report['retrieval_metrics']['hit_at_5']}%")
    print(f"  Mean Reciprocal Rank(MRR): {report['retrieval_metrics']['mrr']}")
    print(f"  Avg Retrieval Latency    : {report['retrieval_metrics']['avg_retrieval_latency_ms']} ms")

    print("\n[Grounding & Citation Integrity]")
    print(f"  Evidence Grounding Rate  : {report['grounding_and_citations']['grounding_rate']}%")
    print(f"  Total Citations Checked  : {report['grounding_and_citations']['total_citations_inspected']}")
    print(f"  Valid Citation Rate      : {report['grounding_and_citations']['valid_citation_rate']}%")
    print(f"  Invalid Citation Rate    : {report['grounding_and_citations']['invalid_citation_rate']}%")

    print("\n[Safety & Hallucination Resistance]")
    print(f"  Hallucination Resistance : {report['safety_and_security']['hallucination_resistance_rate']}%")
    print(f"  Adversarial Defense Rate : {report['safety_and_security']['adversarial_defense_rate']}%")

    print("\n[Multilingual Distribution]")
    for lang, stat in report['multilingual_breakdown'].items():
        print(f"  - [{lang.upper()}] Queries: {stat['total']} | Retrieval Hits: {stat['retrieval_hits']} | Grounded: {stat['grounded']}")

    # Save output report JSON
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "evaluation"))
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, "evaluation_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nSaved detailed evaluation report to: {report_file}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
