# CryptoSentinator Test Suite Documentation

This directory contains the automated tests for the `cryptosentinator` project, written using the `pytest` framework.

## How to Run Tests

1.  Ensure you have installed the test dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  From the root directory of the project (the one containing `cryptosentinator/` and `tests/`), run `pytest`:
    ```bash
    pytest -v
    ```
    The `-v` flag provides verbose output.

## Test Strategy

Our testing strategy is divided into three layers to ensure correctness at every level of the system:

### 1. Tool Unit Tests (`test_tools.py`)

-   **Purpose:** To verify that each individual tool functions correctly in isolation.
-   **Method:** We call each tool function with sample inputs and assert that the output conforms to the expected data structure (schema) and type.
-   **LLM Testing:** For the LLM-based tool (`analyze_sentiment_and_extract_entities`), the test does make a real API call to OpenAI. Its purpose is not to check for specific content but to **validate the schema** of the response. We ensure it returns a dictionary with the correct keys (`sentiment_score`, `sentiment_label`, `entities`) and data types. This test is skipped if the `OPENAI_API_KEY` is not available.

### 2. Agent Unit Tests (`test_agents.py`)

-   **Purpose:** To test the logic of each agent independently of its tool dependencies.
-   **Method:** We use **mocking** (via `pytest-mock`) to replace the agent's tools with mock objects. This allows us to provide controlled, predictable return values from the "tools" and assert that the agent processes this data correctly and returns the expected update to the graph's state. This makes tests fast, deterministic, and free of external API calls.

### 3. Graph Integration Test (`test_graph_integration.py`)

-   **Purpose:** To verify that the entire LangGraph workflow runs from start to finish without errors.
-   **Method:** We test the compiled LangGraph application (`app`) by running it with initial input. This test ensures that:
    -   The nodes (agents) are connected correctly.
    -   The state is passed and updated properly between agents.
    -   The system produces a final output in the expected format.
-   **Dependencies:** This test uses the actual (mocked) tools, simulating a full, real-world run of the system as defined in `main.py`.

### Shared Fixtures (`conftest.py`)

This file defines reusable data fixtures that can be injected into any test function. For example, it provides pre-made `RawDocument` and `ProcessedDocument` objects, reducing code duplication in tests.