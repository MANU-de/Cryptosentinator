import pytest
from cryptosentinator.agents import scout_agent, intelligence_analyst_agent
from cryptosentinator.interactive_pipeline import create_interactive_pipeline # Used for E2E

def test_scout_to_analyst_integration(mocker):
    """
    Integration Test: Verifies that the Analyst Agent can correctly process
    the output produced by the Scout Agent.
    """
    # Arrange: Mock the external tools for both agents
    mocker.patch('cryptosentinator.agents.scout_agent.search_x_mock.invoke', return_value=[{"source": "X", "content": "x_content", "timestamp": "", "keyword": "BTC"}])
    mocker.patch('cryptosentinator.agents.scout_agent.search_reddit_mock.invoke', return_value=[{"source": "Reddit", "content": "reddit_content", "timestamp": "", "keyword": "BTC"}])
    mocker.patch('cryptosentinator.agents.scout_agent.search_news_mock.invoke', return_value=[])

    mock_analyze_tool = mocker.patch('cryptosentinator.agents.intelligence_analyst_agent.analyze_text_deeply')
    mock_analyze_tool.invoke.return_value = {
        "sentiment_score": 0.5, "sentiment_label": "Positive", "topic": "Test", "entities": []
    }

    # Act Part 1: Run the Scout Agent to get its actual output
    scout_state = {"keywords": ["BTC"]}
    scout_result = scout_agent.scout_agent.run(scout_state)
    
    # Act Part 2: Use the Scout's output as the input for the Analyst Agent
    analyst_state = {"raw_documents": scout_result["raw_documents"]}
    analyst_result = intelligence_analyst_agent.intelligence_analyst_agent.run(analyst_state)

    # Assert
    # Check that the handoff was successful
    assert "processed_documents" in analyst_result
    assert len(analyst_result["processed_documents"]) == 2 # 1 from X, 1 from Reddit
    # Check that the analyst's tool was called for each document
    assert mock_analyze_tool.invoke.call_count == 2
    # Check the structure of the processed documents
    assert "sentiment_score" in analyst_result["processed_documents"][0]
    assert analyst_result["processed_documents"][0]["topic"] == "Test"


def test_full_pipeline_end_to_end(mocker):
    """
    End-to-End Test: Verifies that the entire LangGraph pipeline can run
    from start to finish without crashing, given mocked external tools.
    """
    # Arrange: Mock ALL external dependencies across the entire pipeline
    # Scout's tools
    mocker.patch('cryptosentinator.agents.scout_agent.search_x_mock.invoke', return_value=[{"source": "X", "content": "x_content", "timestamp": "", "keyword": "Bitcoin"}])
    mocker.patch('cryptosentinator.agents.scout_agent.search_reddit_mock.invoke', return_value=[])
    mocker.patch('cryptosentinator.agents.scout_agent.search_news_mock.invoke', return_value=[])

    # Analyst's tool
    mocker.patch('cryptosentinator.agents.intelligence_analyst_agent.analyze_text_deeply.invoke', return_value={"sentiment_score": 0.8, "sentiment_label": "Positive", "topic": "Tech", "entities": []})

    # Strategist's tools
    mocker.patch('cryptosentinator.agents.strategist_agent.get_mock_crypto_price_data.invoke', return_value={"price": 1, "24h_change_percent": 1})
    mock_parser = mocker.patch('cryptosentinator.agents.strategist_agent.JsonOutputParser')
    mock_parser_instance = mock_parser.return_value
    mock_parser_instance.invoke.return_value = {"cryptocurrency": "Bitcoin", "hypothesis": "E2E Test Success", "confidence": "High", "reasoning": "", "supporting_evidence": []}

    # Evaluator's tool
    mocker.patch('cryptosentinator.agents.evaluator_agent.get_mock_market_outcome.invoke', return_value="Positive outcome")

    # Act: Run the entire pipeline function
    final_report = create_interactive_pipeline("Bitcoin")

    # Assert: Check that the final output is a valid report string
    assert isinstance(final_report, str)
    assert "Analysis Report for: Bitcoin" in final_report
    assert "E2E Test Success" in final_report
    assert "Performance Evaluation" in final_report
    assert "Correct" in final_report or "Incorrect" in final_report # Check that evaluation ran