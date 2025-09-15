import logging
from typing import List
from graph_state import GraphState, ProcessedDocument
from tools.nlp_tools import analyze_text_deeply

logger = logging.getLogger(__name__)

class IntelligenceAnalystAgent:
    """The Analyst Agent processes raw data to extract sentiment, entities, and topics."""
    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Intelligence Analyst ---")
        raw_documents = state["raw_documents"]
        batch_inputs = [{"text_content": doc["content"]} for doc in raw_documents]
        
        logger.info(f"Starting parallel NLP analysis for {len(batch_inputs)} documents.")
        batch_results = analyze_text_deeply.batch(batch_inputs)
        logger.info("Parallel analysis complete.")

        processed_docs: List[ProcessedDocument] = []
        for doc, result in zip(raw_documents, batch_results):
            # Defensive check: if result is a string, parse it as JSON
            if isinstance(result, str):
                import json
                try:
                    result = json.loads(result)
                except Exception as e:
                    logger.error(f"Failed to parse analysis result JSON: {e}")
                    result = {"sentiment_score": 0.0, "sentiment_label": "Neutral", "topic": "Unclassified", "entities": []}
            processed_docs.append(ProcessedDocument(
                **doc,
                sentiment_score=result.get("sentiment_score"),
                sentiment_label=result.get("sentiment_label"),
                topic=result.get("topic"),
                entities=result.get("entities")
            ))
        return {"processed_documents": processed_docs}

intelligence_analyst_agent = IntelligenceAnalystAgent()