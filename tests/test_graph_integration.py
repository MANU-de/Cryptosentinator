# tests/test_graph_integration.py
import pytest
import os
from langgraph.graph import END
from cryptosentinator.main import run_sentiment_analysis_system

# Mark this module to be skipped if the API key is not present,
# as the full run invokes the NLP tool which requires the key.
pytestmark = pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set for integration test")

def test_full_graph_run():
    """
    Tests the full execution of the LangGraph from start to finish.
    This is an integration test that ensures all nodes connect and
    the state flows correctly.
    """
    keywords = ["IntegrationTestCoin"]
    
    # run_sentiment_analysis_system compiles and runs the app
    final_state = run_sentiment_analysis_system(keywords)

    # 1. Check if the process completed successfully
    assert final_state is not None
    assert final_state.get("error_message") is None

    # 2. Check the final state for expected outputs
    # Check if raw documents were harvested
    assert "raw_documents" in final_state
    assert len(final_state["raw_documents"]) > 0
    assert final_state["raw_documents"][0]["keyword"] == keywords[0]

    # Check if documents were processed
    assert "processed_documents" in final_state
    assert len(final_state["processed_documents"]) > 0
    processed_doc = final_state["processed_documents"][0]
    assert "sentiment_score" in processed_doc
    assert processed_doc["sentiment_score"] is not None

    # Check if insights were generated
    assert "market_insights" in final_state
    assert len(final_state["market_insights"]) > 0
    insight = final_state["market_insights"][0]
    assert insight["cryptocurrency"] == keywords[0]
    assert "overall_sentiment_score" in insight
    assert "correlation_notes" in insight