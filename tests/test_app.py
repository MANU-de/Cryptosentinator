

import pytest
import gradio as gr
from app import demo  # Import the demo object from your app.py
from interactive_pipeline import create_interactive_pipeline

# --- Test 1: Corrected ---
def test_gradio_interface_builds_correctly():
    """
    Tests that the Gradio Blocks object is created and contains the expected components.
    This replaces the 'assert False' placeholder.
    """
    # Assert that the main demo object is a Gradio Blocks instance
    assert isinstance(demo, gr.Blocks)
    
    # Check if key components exist by finding them in the object's structure
    all_components = [block for block in demo.blocks.values()]
    
    # Check for a Textbox component
    assert any(isinstance(comp, gr.Textbox) for comp in all_components), "Textbox input is missing."
    
    # Check for a Button component
    assert any(isinstance(comp, gr.Button) for comp in all_components), "Analyze button is missing."
    
    # Check for a Markdown component for the output
    assert any(isinstance(comp, gr.Markdown) for comp in all_components), "Markdown output is missing."

# --- Test 2: Corrected (This test is now more meaningful) ---
def test_api_name_is_registered():
    """
    Tests that the 'analyze' API endpoint is correctly registered in the app's config.
    This is a valid way to check for the API without making a live call.
    """
    # The app's config contains information about all registered functions and APIs
    app_config = demo.get_config_file()
    
    # Find the dependency corresponding to our button click
    analyze_dependency = None
    for dep in app_config.get("dependencies", []):
        if dep.get("api_name") == "analyze":
            analyze_dependency = dep
            break
            
    assert analyze_dependency is not None, "API with name 'analyze' was not found in the Gradio config."

# --- Test 3: Corrected ---
def test_pipeline_handles_no_api_key_gracefully(mocker):
    """
    Tests that the pipeline returns a user-friendly error string
    when the GEMINI_API_KEY is not set, instead of raising an exception.
    """
    # Arrange: Mock the environment variable to ensure it's missing
    mocker.patch('interactive_pipeline.GEMINI_API_KEY', None)
    
    # Act: Call the function
    result = create_interactive_pipeline("Bitcoin")
    
    # Assert: Check that the return value is the expected error message
    assert "Error" in result
    assert "GEMINI_API_KEY` is not set" in result