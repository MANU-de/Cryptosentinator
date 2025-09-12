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
        processed_docs = []
        for doc in raw_documents:
            nlp_results = analyze_text_deeply.invoke({"text_content": doc["content"]})
            processed_docs.append(ProcessedDocument(
                **doc,
                sentiment_score=nlp_results.get("sentiment_score"),
                sentiment_label=nlp_results.get("sentiment_label"),
                topic=nlp_results.get("topic"),
                entities=nlp_results.get("entities")
            ))
        return {"processed_documents": processed_docs}
    
    # --- NEW: Performance Optimization using .batch() for parallel execution ---
        # Prepare a list of inputs for the batch call
        batch_inputs = [{"text_content": doc["content"]} for doc in raw_documents]
        
        logger.info(f"Starting parallel NLP analysis for {len(batch_inputs)} documents.")
        # The .batch() method runs the tool calls concurrently
        batch_results = analyze_text_deeply.batch(batch_inputs)
        logger.info("Parallel analysis complete.")

        processed_docs: List[ProcessedDocument] = []
        # Combine original documents with the results
        for doc, result in zip(raw_documents, batch_results):
            processed_docs.append(ProcessedDocument(
                **doc,
                sentiment_score=result.get("sentiment_score"),
                sentiment_label=result.get("sentiment_label"),
                topic=result.get("topic"),
                entities=result.get("entities")
            ))
            
        return {"processed_documents": processed_docs}

intelligence_analyst_agent = IntelligenceAnalystAgent()