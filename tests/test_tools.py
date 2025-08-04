import pytest
from cryptosentinator.tools import nlp_tools, market_data_tools
from cryptosentinator.graph_state import RawDocument

def test_analyze_text_deeply_success(mocker):
    """Tests the deep NLP tool by calling its .invoke() method."""
    # Arrange: Patch the 'model' object WHERE IT IS USED - inside the nlp_tools module.
    mock_model = mocker.patch('cryptosentinator.tools.nlp_tools.model')
    
    mock_response_dict = {
        "sentiment_score": 0.8,
        "sentiment_label": "Positive",
        "entities": ["Bitcoin", "SEC"],
        "topic": "Regulation"
    }
    
    # Configure the mock's chain behavior.
    # The chain is `prompt | model | parser`. We can mock the final parser's output.
    mock_parser = mocker.patch('cryptosentinator.tools.nlp_tools.extract_json_from_response', return_value=mock_response_dict)
    #mock_parser_instance = mock_parser.return_value
    #mock_parser_instance.return_value = mock_response_dict

    class MockResponse:
        def __init__(self, text):
            self.text = text

    mock_response_text = '{"sentiment_score": 0.8, "sentiment_label": "Positive", "entities": ["Bitcoin", "SEC"], "topic": "Regulation"}'
    mock_model.generate_content.return_value = MockResponse(mock_response_text)
    
    # Act: Call the decorated tool's .invoke() method, which is what agents do.
    result = nlp_tools.analyze_text_deeply.invoke({"text_content": "Some text."})

    # Assert
    assert result == mock_response_dict

def test_analyze_text_deeply_failure_fallback(mocker):
    """Tests the deep NLP tool's fallback by calling .invoke()."""
    # Arrange: Simulate an error during the chain execution by mocking the model.
    mock_model = mocker.patch('cryptosentinator.tools.nlp_tools.model')
    mock_model.generate_content.side_effect = Exception("API Error")

    # Act: Call the decorated tool's .invoke() method.
    result = nlp_tools.analyze_text_deeply.invoke({"text_content": "Some text."})

    # Assert
    assert result["sentiment_score"] == 0.0
    assert result["topic"] == "Unclassified"

@pytest.mark.parametrize("doc_dicts, expected_substring", [
    ([{"content": "great news moon rocket", "source": "X", "timestamp": "", "keyword": "BTC"}] * 3, "Positive price movement"),
    ([{"content": "scam drop sell", "source": "X", "timestamp": "", "keyword": "BTC"}] * 3, "Negative price movement"),
    ([{"content": "neutral discussion", "source": "X", "timestamp": "", "keyword": "BTC"}], "Stable/Mixed price movement"),
])
def test_get_mock_market_outcome(doc_dicts, expected_substring):
    """
    Tests the mock market outcome logic with correctly typed Pydantic models.
    """
    # Arrange: Convert the list of dicts into a list of RawDocument objects.
    # THIS IS THE FIX FOR THE PYDANTIC VALIDATION ERROR.
    typed_docs = [RawDocument(**doc) for doc in doc_dicts]

    # Act: Call the .invoke() method with the correctly typed data.
    outcome = market_data_tools.get_mock_market_outcome.invoke({"raw_documents": typed_docs})
    
    # Assert
    assert expected_substring in outcome
