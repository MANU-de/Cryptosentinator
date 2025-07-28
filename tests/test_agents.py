# tests/test_agents.py

import pytest
from cryptosentinator.agents import scout_agent, intelligence_analyst_agent, strategist_agent, evaluator_agent

def test_scout_agent(mocker):
    """Tests if the Scout Agent correctly calls its tools and aggregates results."""
    # Arrange
    mocker.patch('cryptosentinator.agents.scout_agent.search_x_mock.invoke', return_value=[{"source": "X", "content": "x", "timestamp": "", "keyword": "BTC"}])
    mocker.patch('cryptosentinator.agents.scout_agent.search_reddit_mock.invoke', return_value=[{"source": "Reddit", "content": "r", "timestamp": "", "keyword": "BTC"}])
    mocker.patch('cryptosentinator.agents.scout_agent.search_news_mock.invoke', return_value=[{"source": "News", "content": "n", "timestamp": "", "keyword": "BTC"}])
    
    initial_state = {"keywords": ["BTC"]}

    # Act
    result_state = scout_agent.scout_agent.run(initial_state)

    # Assert
    assert len(result_state["raw_documents"]) == 3
    assert result_state["raw_documents"][0]["source"] == "X"

def test_intelligence_analyst_agent(mocker, mock_raw_docs):
    """Tests if the Analyst Agent processes documents correctly."""
    # Arrange
    mock_tool = mocker.patch('cryptosentinator.agents.intelligence_analyst_agent.analyze_text_deeply.invoke')
    mock_tool.side_effect = [
        {"sentiment_score": 0.9, "sentiment_label": "Positive", "topic": "Price", "entities": []},
        {"sentiment_score": -0.7, "sentiment_label": "Negative", "topic": "Community", "entities": []}
    ]
    initial_state = {"raw_documents": mock_raw_docs}

    # Act
    result_state = intelligence_analyst_agent.intelligence_analyst_agent.run(initial_state)

    # Assert
    assert len(result_state["processed_documents"]) == 2
    assert result_state["processed_documents"][0]["sentiment_score"] == 0.9
    assert result_state["processed_documents"][1]["topic"] == "Community"
    assert mock_tool.call_count == 2

def test_strategist_agent(mocker, mock_processed_docs):
    """Tests if the Strategist Agent correctly forms a hypothesis."""
    # Arrange
    mocker.patch('cryptosentinator.agents.strategist_agent.get_mock_crypto_price_data.invoke', return_value={"price": 1, "24h_change_percent": 1})
    
    mock_llm_summary = {"cryptocurrency": "Bitcoin", "hypothesis": "Test", "confidence": "High", "reasoning": "Test", "supporting_evidence": []}
    # Mock the entire chain that produces the final JSON
    mocker.patch('cryptosentinator.agents.strategist_agent.JsonOutputParser.invoke', return_value=mock_llm_summary)

    initial_state = {"processed_documents": mock_processed_docs, "keywords": ["Bitcoin"]}

    # Act
    result_state = strategist_agent.strategist_agent.run(initial_state)

    # Assert
    summary = result_state["strategic_summaries"][0]
    assert summary["hypothesis"] == "Test"
    assert summary["confidence"] == "High"

@pytest.mark.parametrize("hypothesis, outcome, expected_result, expected_notes_substr", [
    ("bullish increase", "Positive price movement (+5%)", "Correct", "correctly predicted"),
    ("bearish decrease", "Negative price movement (-5%)", "Correct", "correctly predicted"),
    ("neutral stable", "Stable/Mixed price movement (0.5%)", "Correct", "correctly matched"),
    ("bullish increase", "Negative price movement (-5%)", "Incorrect", "did not match"),
    ("bearish decrease", "Positive price movement (+5%)", "Incorrect", "did not match"),
    ("bullish increase", "Stable/Mixed price movement (0.5%)", "Partially Correct", "predicted a strong move"),
])
def test_evaluator_agent(mocker, mock_strategist_summary, hypothesis, outcome, expected_result, expected_notes_substr):
    """Tests the Evaluator Agent's logic across multiple scenarios."""
    # Arrange
    mock_strategist_summary["hypothesis"] = hypothesis
    mocker.patch('cryptosentinator.agents.evaluator_agent.get_mock_market_outcome.invoke', return_value=outcome)
    
    initial_state = {"strategic_summaries": [mock_strategist_summary], "raw_documents": []}
    
    # Act
    result_state = evaluator_agent.evaluator_agent.run(initial_state)
    evaluation = result_state["evaluation"]

    # Assert
    assert evaluation["evaluation_result"] == expected_result
    assert expected_notes_substr in evaluation["evaluation_notes"]