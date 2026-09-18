import pytest
from app.evaluation.evaluator import RAGEvaluator


@pytest.mark.asyncio
async def test_rag_evaluation_runner_structure():
    evaluator = RAGEvaluator()
    dataset = evaluator.load_dataset()
    assert len(dataset) >= 20

    # Test individual categories present
    categories = {c.get("category") for c in dataset}
    assert "standard_discovery" in categories
    assert "product_to_standard" in categories
    assert "certification" in categories
    assert "laboratory" in categories
    assert "no_evidence" in categories
    assert "adversarial" in categories
    assert "multilingual_consistency" in categories
