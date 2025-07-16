# tests/conftest.py
import pytest
from cryptosentinator.graph_state import RawDocument, ProcessedDocument

@pytest.fixture
def sample_raw_documents():
    """Provides a list of sample RawDocument objects for testing."""
    return [
        RawDocument(
            source="X",
            content="Bitcoin is going to the moon! #BTC 🚀",
            timestamp="2023-10-27T10:00:00Z",
            keyword="Bitcoin"
        ),
        RawDocument(
            source="Reddit",
            content="I am worried about the recent dip in Ethereum's price.",
            timestamp="2023-10-27T11:00:00Z",
            keyword="Ethereum"
        )
    ]

@pytest.fixture
def sample_processed_documents():
    """Provides a list of sample ProcessedDocument objects for testing."""
    return [
        ProcessedDocument(
            source="X",
            content="Bitcoin is going to the moon! #BTC 🚀",
            timestamp="2023-10-27T10:00:00Z",
            keyword="Bitcoin",
            sentiment_score=0.85,
            sentiment_label="Positive",
            entities=["Bitcoin", "BTC"]
        ),
        ProcessedDocument(
            source="News",
            content="Bitcoin market shows signs of stability amidst global uncertainty.",
            timestamp="2023-10-27T09:00:00Z",
            keyword="Bitcoin",
            sentiment_score=0.2,
            sentiment_label="Neutral",
            entities=["Bitcoin"]
        )
    ]