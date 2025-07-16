# tests/test_tools.py
import pytest
import os
from cryptosentinator.tools.web_search_tools import search_x_mock, search_reddit_mock, search_news_mock
from cryptosentinator.tools.market_data_tools import get_mock_crypto_price_data
from cryptosentinator.tools.nlp_tools import analyze_sentiment_and_extract_entities

# --- Web Search Tool Tests ---
def test_search_x_mock():
    keyword = "TestCoin"
    results = search_x_mock.invoke({"keyword": keyword})
    assert isinstance(results, list)
    assert len(results) > 0
    first_result = results[0]
    assert isinstance(first_result, dict)
    assert "source" in first_result
    assert "content" in first_result
    assert first_result["source"] == "X"
    assert keyword in first_result["keyword"]

def test_search_reddit_mock():
    keyword = "TestCoin"
    results = search_reddit_mock.invoke({"keyword": keyword})
    assert isinstance(results, list)
    assert len(results) > 0
    first_result = results[0]
    assert first_result["source"] == "Reddit"
    assert "content" in first_result

def test_search_news_mock():
    keyword = "TestCoin"
    results = search_news_mock.invoke({"keyword": keyword})
    assert isinstance(results, list)
    assert len(results) > 0
    first_result = results[0]
    assert first_result["source"] == "NewsOutlet"
    assert "content" in first_result

# --- Market Data Tool Test ---
def test_get_mock_crypto_price_data():
    symbol = "TC"
    result = get_mock_crypto_price_data.invoke({"cryptocurrency_symbol": symbol})
    assert isinstance(result, dict)
    assert result["symbol"] == symbol
    assert "price" in result and isinstance(result["price"], float)
    assert "24h_change_percent" in result and isinstance(result["24h_change_percent"], float)

# --- NLP Tool Test (Schema Validation) ---
# This test makes a real API call to validate the response schema.
# It will be skipped if the OPENAI_API_KEY is not set.
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
def test_analyze_sentiment_and_extract_entities_schema():
    text = "I think Solana (SOL) has great potential for the future."
    result = analyze_sentiment_and_extract_entities.invoke({"text_content": text})
    
    assert isinstance(result, dict)
    assert "sentiment_score" in result
    assert "sentiment_label" in result
    assert "entities" in result
    
    assert isinstance(result["sentiment_score"], float)
    assert result["sentiment_score"] >= -1.0 and result["sentiment_score"] <= 1.0
    assert isinstance(result["sentiment_label"], str)
    assert result["sentiment_label"] in ["Positive", "Negative", "Neutral"]
    assert isinstance(result["entities"], list)