# Testing Guide for CryptoSentinator v2

This guide provides instructions and best practices for running and writing tests for the `CryptoSentinator v2` project using the `pytest` framework.

## Testing Philosophy

Our testing strategy is centered on unit testing, which ensures that each component (agent or tool) functions correctly in isolation. This approach is crucial for building a reliable and maintainable multi-agent system.

-   **Isolation:** Tests focus on a single unit. External dependencies, particularly network-based services like the OpenAI API, are mocked to ensure tests are fast, deterministic, and free to run.
-   **Readability:** We use `pytest`'s simple `assert` statements and powerful fixture model to create tests that are clean and easy to understand.
-   **Fixtures:** Reusable setup code and data are managed by `pytest` fixtures. This avoids code duplication and makes tests more modular.
-   **Parametrization:** For components with multiple logical branches (like the `EvaluatorAgent`), we use `pytest.mark.parametrize` to run the same test function with different inputs, leading to comprehensive and efficient test coverage.

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
pytest

```
or
```bash
PYTHONPATH=. pytest --maxfail=5 --disable-warnings -q --cov
