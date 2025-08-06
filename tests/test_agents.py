import pytest
from cryptosentinator.agents import scout_agent, intelligence_analyst_agent, strategist_agent, evaluator_agent

def test_scout_agent(mocker):
    """Tests if the Scout Agent correctly calls its tools and aggregates results."""
    mock_x_tool = mocker.patch('cryptosentinator.agents.scout_agent.search_x_mock')
    mock_reddit_tool = mocker.patch('cryptosentinator.agents.scout_agent.search_reddit_mock')
    mock_news_tool = mocker.patch('cryptosentinator.agents.scout_agent.search_news_mock')
    mock_x_tool.invoke.return_value = [{"source": "X", "content": "x", "timestamp": "", "keyword": "BTC"}]
    mock_reddit_tool.invoke.return_value = [{"source": "Reddit", "content": "r", "timestamp": "", "keyword": "BTC"}]
    mock_news_tool.invoke.return_value = [{"source": "News", "content": "n", "timestamp": "", "keyword": "BTC"}]
    initial_state = {"keywords": ["BTC"]}
    result_state = scout_agent.scout_agent.run(initial_state)
    assert len(result_state["raw_documents"]) == 3

def test_intelligence_analyst_agent(mocker, mock_raw_docs):
    """Tests if the Analyst Agent processes documents correctly."""
    mock_analyze_tool = mocker.patch('cryptosentinator.agents.intelligence_analyst_agent.analyze_text_deeply')
    mock_analyze_tool.invoke.side_effect = [
        {"sentiment_score": 0.9, "sentiment_label": "Positive", "topic": "Price", "entities": []},
        {"sentiment_score": -0.7, "sentiment_label": "Negative", "topic": "Community", "entities": []}
    ]
    initial_state = {"raw_documents": mock_raw_docs}
    result_state = intelligence_analyst_agent.intelligence_analyst_agent.run(initial_state)
    assert len(result_state["processed_documents"]) == 2

def test_strategist_agent(mocker, mock_processed_docs):
    """Tests if the Strategist Agent correctly forms a hypothesis."""
    # Arrange
    # CORRECT: Mock the entire tool object where it is used.
    mock_price_tool = mocker.patch('cryptosentinator.agents.strategist_agent.get_mock_crypto_price_data')
    mock_price_tool.invoke.return_value = {"price": 1, "24h_change_percent": 1}
    
    # CORRECT: Mock the generate_content method directly to control the output.
    mock_generate_content = mocker.patch('cryptosentinator.agents.strategist_agent.model.generate_content')
    mock_response_text = '{"cryptocurrency": "Bitcoin", "hypothesis": "Test", "confidence": "High", "reasoning": "Test", "supporting_evidence": []}'
    
    class MockResponse:
        def __init__(self, text):
            self.text = text

    mock_generate_content.return_value = MockResponse(mock_response_text)

    initial_state = {"processed_documents": mock_processed_docs, "keywords": ["Bitcoin"]}

    # Act
    result_state = strategist_agent.strategist_agent.run(initial_state)

    # Assert
    summary = result_state["strategic_summaries"][0]
    assert summary["hypothesis"] == "Test"
    assert summary["confidence"] == "High"
    mock_price_tool.invoke.assert_called_once() # Verify the tool was called.

@pytest.mark.parametrize("hypothesis, outcome, expected_result, expected_notes_substr", [
    ("bullish increase", "Positive price movement (+5%)", "Correct", "correctly predicted"),
    ("bearish decrease", "Negative price movement (-5%)", "Correct", "correctly predicted"),
    ("neutral stable", "Stable/Mixed price movement (0.5%)", "Correct", "correctly matched"),
])
def test_evaluator_agent(mocker, mock_strategist_summary, hypothesis, outcome, expected_result, expected_notes_substr):
    """Tests the Evaluator Agent's logic across multiple scenarios."""
    mock_strategist_summary["hypothesis"] = hypothesis
    mock_outcome_tool = mocker.patch('cryptosentinator.agents.evaluator_agent.get_mock_market_outcome')
    mock_outcome_tool.invoke.return_value = outcome
    initial_state = {"strategic_summaries": [mock_strategist_summary], "raw_documents": []}
    result_state = evaluator_agent.evaluator_agent.run(initial_state)
    evaluation = result_state["evaluation"]
    assert evaluation["evaluation_result"] == expected_result
    assert expected_notes_substr in evaluation["evaluation_notes"]
