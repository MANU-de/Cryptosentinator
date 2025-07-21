# graph_state.py
from typing import List, Dict, TypedDict, Optional

class RawDocument(TypedDict):
    source: str
    content: str
    timestamp: str 
    keyword: str

class ProcessedDocument(RawDocument):
    sentiment_score: Optional[float]
    sentiment_label: Optional[str] # Positive, Negative, Neutral
    topic: Optional[str] # New field: e.g., "Technology", "Regulation", "Price Speculation"
    entities: Optional[List[str]]
    
    class StrategicSummary(TypedDict):
     cryptocurrency: str
    hypothesis: str # e.g., "Strong bullish sentiment driven by tech updates suggests potential short-term price increase."
    confidence: str # e.g., "High", "Medium", "Low"
    reasoning: str
    supporting_evidence: List[Dict] # Snippets from processed docs
    
    class PerformanceEvaluation(TypedDict):
     cryptocurrency: str
    hypothesis_tested: str
    simulated_outcome: str # e.g., "Positive price movement (+5.2%)"
    evaluation_result: str # e.g., "Correct", "Incorrect", "Partially Correct"
    evaluation_notes: str

#class MarketInsight(TypedDict):
    #cryptocurrency: str
    #overall_sentiment_score: float
    #sentiment_trend: str # e.g., "Improving", "Declining", "Stable"
    #correlation_notes: List[str]
    #key_articles_or_posts: List[Dict] # e.g., {'content': '..', 'sentiment': 0.8}

class GraphState(TypedDict):
    keywords: List[str]
    raw_documents: List[RawDocument]
    processed_documents: List[ProcessedDocument]
    strategic_summaries: List[StrategicSummary] # Changed from market_insights
    #market_insights: List[MarketInsight]
    evaluation: Optional[PerformanceEvaluation]
    error_message: Optional[str]
    #current_cryptocurrency: Optional[str] # For correlation