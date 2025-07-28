

import pytest
from cryptosentinator.graph_state import RawDocument, ProcessedDocument, StrategicSummary

@pytest.fixture
def mock_raw_docs():
    """Provides a list of mock RawDocument objects for testing."""
    return [
        RawDocument(source="X", content="Bitcoin to the moon!", timestamp="", keyword="Bitcoin"),
        RawDocument(source="Reddit", content="Feeling bearish about Ethereum.", timestamp="", keyword="Ethereum")
    ]

@pytest.fixture
def mock_processed_docs(mock_raw_docs):
    """Provides a list of mock ProcessedDocument objects for testing."""
    return [
        ProcessedDocument(**mock_raw_docs[0], sentiment_score=0.9, sentiment_label="Positive", topic="Price Speculation", entities=["Bitcoin"]),
        ProcessedDocument(**mock_raw_docs[1], sentiment_score=-0.7, sentiment_label="Negative", topic="Community Discussion", entities=["Ethereum"])
    ]

@pytest.fixture
def mock_strategist_summary():
    """Provides a mock StrategicSummary object for testing the evaluator."""
    return StrategicSummary(
        cryptocurrency="Bitcoin",
        hypothesis="Bullish sentiment suggests a price increase.",
        confidence="High",
        reasoning="Test reasoning.",
        supporting_evidence=[]
    )