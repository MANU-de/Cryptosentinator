import os
import re
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ZeroGPU support with local development fallback
try:
    import spaces
except ImportError:
    class spaces:
        @staticmethod
        def GPU(func=None, **kwargs):
            if func is not None:
                return func
            return lambda f: f

from agents.scout_agent import scout_agent
from agents.intelligence_analyst_agent import intelligence_analyst_agent
from agents.strategist_agent import strategist_agent
from agents.evaluator_agent import evaluator_agent
from graph_state import GraphState


def create_interactive_chart(processed_docs: list, evaluation: dict):
    """Generates an interactive Plotly visualization for sentiment & narratives."""
    narratives = [doc.get("topic", "General") for doc in processed_docs if doc.get("topic")]
    scores = [doc.get("sentiment_score", 0.0) for doc in processed_docs if doc.get("topic")]

    # Shorten long narrative names for clean rendering
    short_narratives = [n[:28] + "..." if len(n) > 28 else n for n in narratives]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Narrative Sentiment Breakdown", "Evaluator Calibration"),
        column_widths=[0.65, 0.35]
    )

    if short_narratives:
        colors = ['#10b981' if s > 0.15 else ('#ef4444' if s < -0.15 else '#94a3b8') for s in scores]
        fig.add_trace(
            go.Bar(
                x=scores,
                y=short_narratives,
                orientation='h',
                marker=dict(color=colors),
                name="Sentiment"
            ),
            row=1, col=1
        )
        fig.update_xaxes(title_text="Score (-1 Bearish to +1 Bullish)", range=[-1.05, 1.05], row=1, col=1)

    # Accuracy Score Indicator
    res_label = evaluation.get("evaluation_result", "N/A")
    score_val = 1.0 if res_label == "Correct" else (0.5 if res_label == "Partially Correct" else 0.0)

    fig.add_trace(
        go.Bar(
            x=[f"Result: {res_label}"],
            y=[score_val],
            marker=dict(color='#6366f1'),
            name="Score"
        ),
        row=1, col=2
    )
    fig.update_yaxes(range=[0, 1.1], title_text="Evaluation Score", row=1, col=2)

    fig.update_layout(
        template="plotly_dark",
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False
    )
    return fig


@spaces.GPU
def stream_pipeline(keyword_input: str):
    """
    Generator function that runs the 4-agent cycle sequentially,
    yielding progressive real-time feedback to the Gradio interface.
    """
    keyword = keyword_input.strip() if keyword_input else "Bitcoin"
    state: GraphState = {
        "keywords": [keyword],
        "raw_documents": [],
        "processed_documents": [],
        "strategic_summaries": []
    }

    # --- Step 1: Scout ---
    yield (
        "### 🛰️ `[1/4]` Scout Agent Active...\n*Fetching live Binance perpetual funding rates, DefiLlama on-chain TVL, and social intelligence...*",
        "",
        None,
        "",
        gr.update(visible=False)
    )
    scout_res = scout_agent.run(state)
    state["raw_documents"] = scout_res["raw_documents"]

    # --- Step 2: Analyst ---
    yield (
        f"### 🧠 `[2/4]` Intelligence Analyst Active...\n*Clustering {len(state['raw_documents'])} documents into crypto narratives and computing source-aware sentiment...*",
        "",
        None,
        "",
        gr.update(visible=False)
    )
    analyst_res = intelligence_analyst_agent.run(state)
    state["processed_documents"] = analyst_res["processed_documents"]

    # --- Step 3: Strategist ---
    yield (
        "### ♟️ `[3/4]` Strategist Agent Active...\n*Formulating multi-timeframe horizon ([24h Tactical], [7d Strategic]) & risk invalidation with Gemini/HF Inference...*",
        "",
        None,
        "",
        gr.update(visible=False)
    )
    strategist_res = strategist_agent.run(state)
    state["strategic_summaries"] = strategist_res["strategic_summaries"]

    # --- Step 4: Evaluator ---
    yield (
        "### ⚖️ `[4/4]` Evaluator Agent Active...\n*Benchmarking against ground truth, updating persistent backtest history, and calculating cumulative win rate...*",
        "",
        None,
        "",
        gr.update(visible=False)
    )
    evaluator_res = evaluator_agent.run(state)
    evaluation = evaluator_res["evaluation"]

    # --- Synthesis & Formatting ---
    summary = state["strategic_summaries"][0]
    processed_docs = state["processed_documents"]

    report_md = f"""# 📊 Intelligence Briefing: {summary['cryptocurrency']}

### 🧠 Strategic Multi-Timeframe Hypothesis
> **Outlook:** {summary['hypothesis']}

* **Confidence Level:** `{summary.get('confidence', 'Medium')}`
* **Institutional Reasoning:**
{summary['reasoning']}

---

### ⚖️ Evaluator Benchmark & Persistent Backtest
* **Simulated Outcome:** `{evaluation.get('simulated_outcome', 'N/A')}`
* **Evaluation Result:** **`{evaluation.get('evaluation_result', 'N/A')}`**
* **Cumulative Track Record:**
{evaluation.get('evaluation_notes', 'N/A')}
"""

    evidence_md = "### 📜 Supporting Evidence & Microstructure Data\n\n"
    for item in summary.get("supporting_evidence", []):
        evidence_md += f"* `{item}`\n"

    # Interactive Chart
    fig = create_interactive_chart(processed_docs, evaluation)

    # Save to export file
    export_filename = f"{keyword.lower()}_intelligence_briefing.md"
    with open(export_filename, "w", encoding="utf-8") as f:
        f.write(report_md + "\n\n" + evidence_md)

    yield (
        f"✅ **Analysis Complete for {keyword}! All 4 agents executed successfully.**",
        report_md,
        fig,
        evidence_md,
        gr.update(value=export_filename, visible=True)
    )


# --- Gradio UI Layout ---
with gr.Blocks(theme=gr.themes.Soft(), title="CryptoSentinator v3") as demo:
    gr.Markdown(
        """
        # 🤖 CryptoSentinator v3: Intelligence & Quantitative Strategy Agent
        Autonomous 4-agent crypto market analysis powered by **live Binance perpetual funding rates**, **DefiLlama on-chain TVL**, **narrative clustering**, and **persistent backtesting**.
        """
    )

    with gr.Accordion("⚠️ Educational & Research Disclaimer", open=False):
        gr.Markdown(
            """
            * This system is strictly for **demonstrational and educational purposes**.
            * Output generated by multi-agent AI and simulated ground-truth testing should **not** be considered financial or investment advice.
            * Always conduct your own research (DYOR) before making capital allocations.
            """
        )

    with gr.Row():
        with gr.Column(scale=4):
            keyword_input = gr.Textbox(
                label="Enter Cryptocurrency Keyword",
                placeholder="e.g., Bitcoin, Ethereum, Solana",
                value="Bitcoin"
            )
        with gr.Column(scale=1):
            analyze_button = gr.Button("🚀 Run Multi-Agent Analysis", variant="primary", scale=1)

    # Live Status Step Bar
    status_box = gr.Markdown("🟢 *Ready. Click 'Run Multi-Agent Analysis' to start the pipeline.*")

    with gr.Tabs():
        with gr.TabItem("📊 Strategic Briefing"):
            output_report = gr.Markdown(label="Strategic Summary")
            export_btn = gr.DownloadButton("📥 Download Full Briefing (.md)", visible=False)

        with gr.TabItem("📈 Interactive Narrative & Metrics Chart"):
            metrics_plot = gr.Plot(label="Sentiment & Evaluation Analytics")

        with gr.TabItem("📜 Supporting Evidence & Market Feeds"):
            evidence_box = gr.Markdown(label="Evidence Details")

    gr.Examples(
        examples=[["Bitcoin"], ["Ethereum"], ["Solana"]],
        inputs=keyword_input
    )

    analyze_button.click(
        fn=stream_pipeline,
        inputs=keyword_input,
        outputs=[status_box, output_report, metrics_plot, evidence_box, export_btn]
    )

if __name__ == "__main__":
    demo.launch()