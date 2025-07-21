
from ..graph_state import GraphState, ProcessedDocument
from ..tools.nlp_tools import analyze_text_deeply

class IntelligenceAnalystAgent:
    """The Analyst Agent processes raw data to extract sentiment, entities, and topics."""
    def run(self, state: GraphState) -> dict:
        print("--- AGENT: Intelligence Analyst ---")
        raw_documents = state["raw_documents"]
        processed_docs = []
        for doc in raw_documents:
            nlp_results = analyze_text_deeply({"text_content": doc["content"]})
            processed_docs.append(ProcessedDocument(
                **doc,
                sentiment_score=nlp_results.get("sentiment_score"),
                sentiment_label=nlp_results.get("sentiment_label"),
                topic=nlp_results.get("topic"),
                entities=nlp_results.get("entities")
            ))
        return {"processed_documents": processed_docs}

intelligence_analyst_agent = IntelligenceAnalystAgent()