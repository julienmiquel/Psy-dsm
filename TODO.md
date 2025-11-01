# TODO

This file outlines the current status of the project and the remaining tasks.

## Completed Work

-   **UI Framework:** The Mesop UI has been replaced with a new Streamlit UI in `src/app/main.py`.
-   **Decoupled API:** The Gemini API integration has been decoupled into a separate `gemini_services.py` module, which is called by the `services.py` module.
-   **Feature Specifications:** Feature specification files have been created in the `specs` directory to document the application's functionality.
-   **Dockerfile:** The `Dockerfile` has been updated to run the Streamlit application.
-   **Tests:** The tests in `tests/test_app.py` have been updated to be compatible with the new architecture.

## Blocker

-   **Streamlit `src` Layout Issue:** The Streamlit application fails to start due to an `ImportError: attempted relative import with no known parent package` error. This is a common issue with Python projects that use a `src` layout, but the standard solutions have not worked in this environment. The application is currently un-runnable due to this unresolved environment or pathing problem.
