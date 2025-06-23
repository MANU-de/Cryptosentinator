# graph_state.py
from typing import List, Dict, TypedDict, Optional

class RawDocument(TypedDict):
    source: str
    content: str
    timestamp: str # ISO format string
    keyword: str

class ProcessedDocument(RawDocument):
    sentiment_score: Optional[float]
    sentiment_label: Optional[str] # Positive, Negative, Neutral
    entities: Optional[List[str]]

class MarketInsight(TypedDict):
    cryptocurrency: str
    overall_sentiment_score: float
    sentiment_trend: str # e.g., "Improving", "Declining", "Stable"
    correlation_notes: List[str]
    key_articles_or_posts: List[Dict] # e.g., {'content': '..', 'sentiment': 0.8}

class GraphState(TypedDict):
    keywords: List[str]
    raw_documents: List[RawDocument]
    processed_documents: List[ProcessedDocument]
    market_insights: List[MarketInsight]
    error_message: Optional[str]
    current_cryptocurrency: Optional[str] # For correlation