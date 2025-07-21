
from typing_extensions import List, Dict, TypedDict, Optional

class RawDocument(TypedDict):
    source: str
    content: str
    timestamp: str 
    keyword: str

class StrategicSummary(TypedDict):
    cryptocurrency: str
    hypothesis: str
    confidence: str
    reasoning: str
    supporting_evidence: List[Dict]

class PerformanceEvaluation(TypedDict):
    cryptocurrency: str
    hypothesis_tested: str
    simulated_outcome: str
    evaluation_result: str
    evaluation_notes: str

class ProcessedDocument(RawDocument):
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    topic: Optional[str]
    entities: Optional[List[str]]

class GraphState(TypedDict):
    keywords: List[str]
    raw_documents: List[RawDocument]
    processed_documents: List[ProcessedDocument]
    strategic_summaries: List[StrategicSummary]
    evaluation: Optional[PerformanceEvaluation]
    error_message: Optional[str]