import pytest
from interactive_pipeline import create_interactive_pipeline

def test_create_interactive_pipeline_called(monkeypatch):
    import interactive_pipeline
    called = {}
    def mock_create_interactive_pipeline(keywords):
        called["keywords"] = keywords
        return "Mocked report"

    monkeypatch.setattr(interactive_pipeline, "create_interactive_pipeline", mock_create_interactive_pipeline)

    result = interactive_pipeline.create_interactive_pipeline("Bitcoin")
    assert result == "Mocked report"
    assert called["keywords"] == "Bitcoin"
