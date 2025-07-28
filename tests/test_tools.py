# tests/test_tools.py

import pytest
from cryptosentinator.tools import nlp_tools, market_data_tools

def test_analyze_text_deeply_success(mocker):
    """Tests the deep NLP tool for a successful LLM response."""
    # Arrange
    mock_llm = mocker.patch('cryptosentinator.tools.nlp_tools.llm')
    mock_response = {
        "sentiment_score": 0.8,
        "sentiment_label": "Positive",
        "entities": ["Bitcoin", "SEC"],
        "topic": "Regulation"
    }
    mock_llm.invoke.return_value = mock_response

    # Act
    result = nlp_tools.analyze_text_deeply.invoke({"text_content": "Some text."})

    # Assert
    assert result == mock_response

def test_analyze_text_deeply_failure_fallback(mocker):
    """Tests the deep NLP tool's fallback mechanism on LLM error."""
    # Arrange
    mocker.patch('cryptosentinator.tools.nlp_tools.llm.invoke', side_effect=Exception("API Error"))

    # Act
    result = nlp_tools.analyze_text_deeply.invoke({"text_content": "Some text."})

    # Assert
    assert result["sentiment_score"] == 0.0
    assert result["topic"] == "Unclassified"

@pytest.mark.parametrize("docs, expected_substring", [
    ([{"content": "great news moon rocket", "source": "X", "timestamp": "", "keyword": "BTC"}] * 3, "Positive price movement"),
    ([{"content": "scam drop sell", "source": "X", "timestamp": "", "keyword": "BTC"}] * 3, "Negative price movement"),
    ([{"content": "neutral discussion", "source": "X", "timestamp": "", "keyword": "BTC"}], "Stable/Mixed price movement"),
])
def test_get_mock_market_outcome(docs, expected_substring):
    """Tests the mock market outcome logic for positive, negative, and neutral scenarios."""
    # Act
    outcome = market_data_tools.get_mock_market_outcome.invoke({"raw_documents": docs})
    
    # Assert
    assert expected_substring in outcome