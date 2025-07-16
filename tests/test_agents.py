# tests/test_agents.py
from cryptosentinator.agents.data_harvester_agent import data_harvester_agent
from cryptosentinator.agents.nlp_processing_agent import nlp_processing_agent
from cryptosentinator.agents.market_correlation_agent import market_correlation_agent
from cryptosentinator.graph_state import GraphState

def test_data_harvester_agent(mocker):
    """Test the Data Harvester Agent by mocking its tools."""
    # Mock the return values of the search tools
    mocker.patch(
        'cryptosentinator.agents.data_harvester_agent.search_x_mock.invoke',
        return_value=[{"source": "X", "content": "x_content", "timestamp": "ts", "keyword": "BTC"}]
    )
    mocker.patch(
        'cryptosentinator.agents.data_harvester_agent.search_reddit_mock.invoke',
        return_value=[{"source": "Reddit", "content": "reddit_content", "timestamp": "ts", "keyword": "BTC"}]
    )
    mocker.patch(
        'cryptosentinator.agents.data_harvester_agent.search_news_mock.invoke',
        return_value=[] # Simulate no news found
    )

    initial_state = GraphState(keywords=["BTC"], raw_documents=[], processed_documents=[], market_insights=[])
    
    result_state = data_harvester_agent.run(initial_state)

    assert "raw_documents" in result_state
    raw_docs = result_state["raw_documents"]
    assert len(raw_docs) == 2
    assert raw_docs[0]["source"] == "X"
    assert raw_docs[1]["source"] == "Reddit"

def test_nlp_processing_agent(mocker, sample_raw_documents):
    """Test the NLP Agent by mocking the NLP tool."""
    # Mock the NLP tool to return a consistent result
    mock_nlp_result = {
        "sentiment_score": 0.9,
        "sentiment_label": "Positive",
        "entities": ["TestEntity"]
    }
    mocker.patch(
        'cryptosentinator.agents.nlp_processing_agent.analyze_sentiment_and_extract_entities.invoke',
        return_value=mock_nlp_result
    )

    initial_state = GraphState(keywords=[], raw_documents=sample_raw_documents, processed_documents=[], market_insights=[])

    result_state = nlp_processing_agent.run(initial_state)

    assert "processed_documents" in result_state
    processed_docs = result_state["processed_documents"]
    assert len(processed_docs) == len(sample_raw_documents)
    
    first_doc = processed_docs[0]
    assert first_doc["sentiment_score"] == mock_nlp_result["sentiment_score"]
    assert first_doc["sentiment_label"] == mock_nlp_result["sentiment_label"]
    assert first_doc["entities"] == mock_nlp_result["entities"]
    assert first_doc["keyword"] == sample_raw_documents[0]["keyword"]


def test_market_correlation_agent(mocker, sample_processed_documents):
    """Test the Market Correlation Agent by mocking the price tool."""
    # Mock the price data tool
    mock_price_data = {"symbol": "Bitcoin", "price": 50000.0, "24h_change_percent": 5.0}
    mocker.patch(
        'cryptosentinator.agents.market_correlation_agent.get_mock_crypto_price_data.invoke',
        return_value=mock_price_data
    )

    initial_state = GraphState(
        keywords=["Bitcoin"],
        raw_documents=[],
        processed_documents=sample_processed_documents,
        market_insights=[]
    )

    result_state = market_correlation_agent.run(initial_state)

    assert "market_insights" in result_state
    insights = result_state["market_insights"]
    assert len(insights) == 1
    
    insight = insights[0]
    assert insight["cryptocurrency"] == "Bitcoin"
    assert "correlation_notes" in insight
    assert len(insight["correlation_notes"]) > 0
    # Check if the mock price made it into the notes
    assert "5.0%" in insight["correlation_notes"][0]