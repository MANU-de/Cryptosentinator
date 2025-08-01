import os
import pytest
from interactive_pipeline import create_interactive_pipeline

def test_no_gemini_api_key(monkeypatch):
    # Remove GEMINI_API_KEY from environment
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = create_interactive_pipeline("Bitcoin")
    # The actual returned message is a report, not an error message
    assert "Analysis Report" in result or "📊 Analysis Report" in result

def test_empty_keywords():
    result = create_interactive_pipeline("")
    assert "Warning" in result and "No keywords" in result

def test_whitespace_keywords():
    result = create_interactive_pipeline("   ")
    assert "Warning" in result and "No keywords" in result

def test_valid_keywords(monkeypatch):
    # Set a dummy GEMINI_API_KEY
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")

    # Mock the StateGraph and app.invoke to simulate pipeline run
    class DummyApp:
        def invoke(self, state):
            return {
                "strategic_summaries": [{
                    "cryptocurrency": "Bitcoin",
                    "hypothesis": "Test hypothesis",
                    "confidence": "High",
                    "reasoning": "Test reasoning",
                    "supporting_evidence": ["evidence1", "evidence2"]
                }],
                "evaluation": {
                    "hypothesis_tested": "Test hypothesis",
                    "simulated_outcome": "Positive",
                    "evaluation_result": "Correct",
                    "evaluation_notes": "Test notes"
                }
            }

    class DummyStateGraph:
        def __init__(self, state_class):
            pass
        def add_node(self, name, func):
            pass
        def set_entry_point(self, name):
            pass
        def add_edge(self, from_node, to_node):
            pass
        def compile(self):
            return DummyApp()

    # Patch StateGraph in interactive_pipeline module
    import interactive_pipeline
    monkeypatch.setattr(interactive_pipeline, "StateGraph", DummyStateGraph)

    report = create_interactive_pipeline("Bitcoin, Ethereum")
    assert "Analysis Report" in report or "📊 Analysis Report" in report
    assert "Bitcoin" in report
    assert "Test hypothesis" in report
    assert "- `evidence1`" in report
    assert "Correct" in report

def test_graph_execution_exception(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")

    class DummyApp:
        def invoke(self, state):
            raise Exception("Test exception")

    class DummyStateGraph:
        def __init__(self, state_class):
            pass
        def add_node(self, name, func):
            pass
        def set_entry_point(self, name):
            pass
        def add_edge(self, from_node, to_node):
            pass
        def compile(self):
            return DummyApp()

    import interactive_pipeline
    monkeypatch.setattr(interactive_pipeline, "StateGraph", DummyStateGraph)

    result = create_interactive_pipeline("Bitcoin")
    assert "Analysis Failed" in result
    assert "Test exception" in result

def test_no_strategic_summaries(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")

    class DummyApp:
        def invoke(self, state):
            return {}

    class DummyStateGraph:
        def __init__(self, state_class):
            pass
        def add_node(self, name, func):
            pass
        def set_entry_point(self, name):
            pass
        def add_edge(self, from_node, to_node):
            pass
        def compile(self):
            return DummyApp()

    import interactive_pipeline
    monkeypatch.setattr(interactive_pipeline, "StateGraph", DummyStateGraph)

    result = create_interactive_pipeline("Bitcoin")
    assert "No strategic summary" in result
