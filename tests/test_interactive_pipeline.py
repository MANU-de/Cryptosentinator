import pytest
from interactive_pipeline import create_interactive_pipeline

def test_create_interactive_pipeline(mocker):
    """Test the interactive pipeline function with mocked agents."""
    # Patch the agents to return fixed outputs
    mocker.patch('interactive_pipeline.scout_agent.run', return_value={"raw_documents": [{"content": "test", "keyword": "BTC", "source": "X", "timestamp": ""}]})
    mocker.patch('interactive_pipeline.intelligence_analyst_agent.run', return_value={"processed_documents": [{"content": "test", "keyword": "BTC", "sentiment_score": 0.5, "sentiment_label": "Positive", "topic": "Test", "entities": []}]})
    mocker.patch('interactive_pipeline.strategist_agent.run', return_value={"strategic_summaries": [{"cryptocurrency": "BTC", "hypothesis": "Test hypothesis", "confidence": "High", "reasoning": "Test reasoning", "supporting_evidence": []}]})
    mocker.patch('interactive_pipeline.evaluator_agent.run', return_value={"evaluation": {"evaluation_result": "Correct", "evaluation_notes": "Test notes"}})

    report = create_interactive_pipeline("BTC")
    assert "Analysis Report for:" in report
    assert "Test hypothesis" in report
    assert "Correct" in report
