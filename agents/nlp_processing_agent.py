# agents/nlp_processing_agent.py
from typing import List
from ..graph_state import GraphState, ProcessedDocument, RawDocument # Relative import
from ..tools.nlp_tools import analyze_sentiment_and_extract_entities # Relative import

class NlpProcessingAgent:
    def __init__(self):
        self.nlp_tool = analyze_sentiment_and_extract_entities

    def run(self, state: GraphState) -> dict:
        print("--- AGENT: NLP Processor Running ---")
        raw_documents = state.get("raw_documents", [])
        if not raw_documents:
            return {"error_message": "No raw documents to process."}

        processed_docs: List[ProcessedDocument] = []
        for doc_dict in raw_documents:
            # Convert dict back to RawDocument if necessary, or ensure it's already typed
            raw_doc = RawDocument(**doc_dict) if isinstance(doc_dict, dict) else doc_dict

            try:
                nlp_results = self.nlp_tool.invoke({"text_content": raw_doc["content"]})
                
                processed_doc = ProcessedDocument(
                    source=raw_doc["source"],
                    content=raw_doc["content"],
                    timestamp=raw_doc["timestamp"],
                    keyword=raw_doc["keyword"],
                    sentiment_score=nlp_results.get("sentiment_score"),
                    sentiment_label=nlp_results.get("sentiment_label"),
                    entities=nlp_results.get("entities")
                )
                processed_docs.append(processed_doc)
            except Exception as e:
                print(f"Error processing document content '{raw_doc['content'][:30]}...': {e}")
                # Add with None for NLP fields to indicate failure for this doc
                processed_docs.append(ProcessedDocument(
                    source=raw_doc["source"],
                    content=raw_doc["content"],
                    timestamp=raw_doc["timestamp"],
                    keyword=raw_doc["keyword"],
                    sentiment_score=None,
                    sentiment_label=None,
                    entities=None
                ))
        
        print(f"Processed {len(processed_docs)} documents with NLP.")
        return {"processed_documents": processed_docs}

nlp_processing_agent = NlpProcessingAgent()