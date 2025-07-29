# app.py

import gradio as gr
from interactive_pipeline import create_interactive_pipeline

# Define the Gradio interface using Blocks for more control
with gr.Blocks(theme=gr.themes.Soft(), title="CryptoSentinator v2") as demo:
    gr.Markdown(
        """
        # 🤖 CryptoSentinator v2: The Specialist Crew
        Enter one or more cryptocurrency keywords (e.g., Bitcoin, Ethereum) to start the multi-agent analysis.
        The system will gather data, analyze sentiment and topics, form a strategic hypothesis, and evaluate its own performance.
        """
    )
    
    with gr.Row():
        keyword_input = gr.Textbox(
            label="Enter Cryptocurrency Keywords (comma-separated)", 
            placeholder="e.g., Bitcoin, Solana, XRP"
        )
    
    analyze_button = gr.Button("🚀 Analyze Sentiment", variant="primary")
    
    gr.Markdown("---") # Divider
    
    output_report = gr.Markdown(label="Analysis Report")
    
    # Define the click action
    analyze_button.click(
        fn=create_interactive_pipeline,
        inputs=keyword_input,
        outputs=output_report,
        api_name="analyze" # Exposes this as an API endpoint
    )
    
    # Add examples for users to try
    gr.Examples(
        examples=[
            ["Bitcoin"],
            ["Ethereum, Regulation"],
            ["Solana"]
        ],
        inputs=keyword_input,
        outputs=output_report,
        fn=create_interactive_pipeline,
        cache_examples=False, # Set to True for faster demo, but may show stale data
    )

# Launch the interface
if __name__ == "__main__":
    demo.launch(share=True)