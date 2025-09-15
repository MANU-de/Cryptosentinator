import pytest
import gradio as gr
import os
from app import demo
from config import get_gemini_api_key
from main import run_crypto_sentinator_v2

def get_all_components(block):
    """Recursively get all components in a Gradio Blocks."""
    components = []
    for child in block.children:
        components.append(child)
        if hasattr(child, 'children') and child.children:
            components.extend(get_all_components(child))
    return components

def test_gradio_interface():
    """Test that the Gradio interface launches and has expected components."""
    assert isinstance(demo, gr.Blocks)
    all_components = get_all_components(demo)
    # Check that the interface has a textbox for keyword input
    keyword_inputs = [comp for comp in all_components if isinstance(comp, gr.Textbox)]
    assert len(keyword_inputs) == 1
    # Check that the interface has a button to trigger analysis
    buttons = [comp for comp in all_components if isinstance(comp, gr.Button)]
    assert any(button.label == "🚀 Analyze Sentiment" for button in buttons)
    # Check that the interface has a markdown output for report
    markdowns = [comp for comp in all_components if isinstance(comp, gr.Markdown)]
    assert any("Analysis Report" in (md.label or "") for md in markdowns)

@pytest.mark.asyncio
async def test_gradio_api_call(monkeypatch):
    """Test the API endpoint exposed by Gradio for analysis."""
    # Patch the create_interactive_pipeline function to return a fixed string
    monkeypatch.setattr("app.create_interactive_pipeline", lambda keyword: f"Mock report for {keyword}")
    # Simulate calling the API function directly
    result = await demo.api.analyze("Bitcoin")
    assert "Mock report for Bitcoin" == result

def test_get_gemini_api_key(monkeypatch):
    """Test the config function to get Gemini API key."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    assert get_gemini_api_key() == "test_key"

def test_run_crypto_sentinator_v2_no_api_key(monkeypatch):
    """Test run_crypto_sentinator_v2 raises error when API key is missing."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
        run_crypto_sentinator_v2(["BTC"])
