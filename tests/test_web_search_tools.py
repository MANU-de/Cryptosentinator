import pytest
from unittest.mock import patch
from tools import web_search_tools

def mock_search_x(keyword, count=5):
    return [
        {"source": "X", "content": f"Great news for #{keyword}!", "timestamp": "2023-01-01T00:00:00", "keyword": keyword}
    ] * count

def mock_search_reddit(keyword, subreddit="cryptocurrency", count=3):
    return [
        {"source": "Reddit", "content": f"Discussion about {keyword}", "timestamp": "2023-01-01T00:00:00", "keyword": keyword}
    ] * count

def mock_search_news(keyword, count=2):
    return [
        {"source": "NewsOutlet", "content": f"Major financial news on {keyword}", "timestamp": "2023-01-01T00:00:00", "keyword": keyword}
    ] * count

@patch('tools.web_search_tools.search_x_mock', side_effect=mock_search_x)
def test_search_x_mock(mock_func):
    results = web_search_tools.search_x_mock("Bitcoin", 3)
    assert isinstance(results, list)
    assert len(results) == 3
    for item in results:
        assert item["source"] == "X"
        assert "Bitcoin" in item["content"]
        assert "keyword" in item
        assert item["keyword"] == "Bitcoin"

@patch('tools.web_search_tools.search_reddit_mock', side_effect=mock_search_reddit)
def test_search_reddit_mock(mock_func):
    results = web_search_tools.search_reddit_mock("Ethereum", "cryptocurrency", 2)
    assert isinstance(results, list)
    assert len(results) == 2
    for item in results:
        assert item["source"] == "Reddit"
        assert "Ethereum" in item["content"]
        assert "keyword" in item
        assert item["keyword"] == "Ethereum"

@patch('tools.web_search_tools.search_news_mock', side_effect=mock_search_news)
def test_search_news_mock(mock_func):
    results = web_search_tools.search_news_mock("Solana", 1)
    assert isinstance(results, list)
    assert len(results) == 1
    for item in results:
        assert item["source"] == "NewsOutlet"
        assert "Solana" in item["content"]
        assert "keyword" in item
        assert item["keyword"] == "Solana"
