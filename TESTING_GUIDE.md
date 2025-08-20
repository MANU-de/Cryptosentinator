# Testing Guide for CryptoSentinator v2

This guide provides instructions and best practices for running and writing tests for the `CryptoSentinator v2` project using the `pytest` framework.

## Testing Philosophy

Our test suite is structured to provide robust coverage at every level:

- **Unit Tests:** These are the foundation. They test each individual function and agent method in complete isolation to ensure its logic is correct. All external dependencies (like LLM calls) are mocked.
- **Integration Tests:** These tests verify the "handoff" between agents. For example, we test that the IntelligenceAnalystAgent can correctly process the exact output format produced by the ScoutAgent. This ensures agents can communicate and work together.
- **End-to-End (E2E) Tests:** This test simulates a full user journey. It runs the entire LangGraph pipeline from start to finish, mocking only the external APIs. This validates that the complete workflow is connected correctly and produces a final report in the expected format.
-   **Parametrization:** For components with multiple logical branches (like the `EvaluatorAgent`), we use `pytest.mark.parametrize` to run the same test function with different inputs, leading to comprehensive and efficient test coverage.

-   We use the pytest-cov library to measure how much of our codebase is executed by our tests.
    High test coverage is a strong indicator of a robust and reliable application. 
    
    Our goal is to maintain a coverage of 90% or higher for all critical application logic.

## Prerequisites & Setup

Before running the tests, you need to install `pytest` and its mocking plugin.

1.  **Activate your virtual environment:**
    ```bash
    source venv/bin/activate  # On macOS/Linux
    .\venv\Scripts\activate   # On Windows
    ```

2.  **Install testing libraries:**
    ```bash
    pip install pytest pytest-mock
    ```

## How to Run Tests

All tests are located in the `tests/` directory (a standard practice). To run the test suite, navigate to the root directory of the project and execute the following command:

```bash
pytest --cov=cryptosentinator

```
or
```bash
PYTHONPATH=. pytest --maxfail=5 --disable-warnings -q --cov
