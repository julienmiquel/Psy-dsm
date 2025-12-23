# Clinical Character Profiling and Analysis System

## Overview

This repository contains a sophisticated Streamlit-based application designed to assist clinical psychologists and career counselors. It leverages Generative AI (specifically Google's Gemini models) to analyze character descriptions and generate detailed clinical profiles, including psychological diagnoses and personality assessments.

## Key Features

### 1. Clinical Profile Generation
The core of the application is the ability to transform a textual description of a character into a structured clinical profile. This profile includes:
-   **DSM-5 Diagnoses:** Identification of potential mental health disorders, complete with DSM-5 codes, specific criteria met, and functional impairment analysis.
-   **Holland Code (RIASEC):** Assessment of professional interests based on the RIASEC model (Realistic, Investigative, Artistic, Social, Enterprising, Conventional).
-   **Big 5 (OCEAN):** *New!* A comprehensive personality evaluation based on the Five Factor Model (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism).

### 2. TCC Program Generation
Beyond assessment, the system can generate a customized Cognitive Behavioral Therapy (TCC) program tailored to the character's specific needs and diagnoses.

### 3. LLM-as-a-Judge Evaluation
To ensure quality and accuracy, the application includes an "LLM-as-a-Judge" module. This feature uses a separate AI model to evaluate the generated profiles against a "golden standard," providing a score and rationale for the quality of the analysis.

### 4. Interactive Chat Mode
Users can interact with the system in a conversational mode to refine assessments or explore specific aspects of a character's psychology.

## Technical Architecture

-   **Frontend:** Built with [Streamlit](https://streamlit.io/), offering a responsive and interactive user interface.
-   **Backend:** Powered by Python, utilizing [Pydantic](https://docs.pydantic.dev/) for robust data validation and modeling.
-   **AI Integration:** Integrates with Google Vertex AI (Gemini) for text generation and analysis.
-   **Infrastructure:** Deployed on Google Cloud Platform (Cloud Run), with infrastructure managed via Terraform.

## Getting Started

1.  **Installation:** Use Poetry to install dependencies: `poetry install`.
2.  **Configuration:** Set up your Google Cloud credentials and environment variables (specifically `GOOGLE_API_KEY` or `GEMINI_API_KEY`).
3.  **Running the App:** Execute `PYTHONPATH=src poetry run streamlit run src/app/main.py`.

## Future Directions

The project is continuously evolving, with plans to incorporate more advanced psychological models and enhance the interactive capabilities of the AI agents.
