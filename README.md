# Psy-dsm
A tool to help to map psychological pathologies based on DSM-5 reference book.

This application uses the Google Gemini API to generate a clinical profile of a fictional character based on a user-provided description. The profile is based on the DSM-5 criteria and is intended for creative and academic purposes.

## Project Structure

- `src/app`: Contains the main application code.
  - `main.py`: The entry point for the Mesop application.
  - `agent.py`:  Handles the interaction with the Gemini API.
  - `models.py`: Defines the Pydantic models for the application.
  - `services.py`:  Contains the business logic of the application.
- `terraform`: Contains the Terraform code for infrastructure as code.
  - `main.tf`:  Defines the Google Cloud Run service and other resources.
  - `variables.tf`:  Defines the variables used in the Terraform configuration.
- `tests`: Contains the tests for the application.
- `cloudbuild.yaml`:  Defines the CI/CD pipeline for building and deploying the application.
- `Dockerfile`:  Used to containerize the application.
- `poetry.lock` and `pyproject.toml`:  Defines the project dependencies.

## How to Run

1.  **Install the dependencies:**

    ```
    poetry install
    ```

2.  **Set your Google API key:**

    ```
    export GOOGLE_API_KEY="YOUR_API_KEY"
    ```

3.  **Run the application:**

    ```
    poetry run mesop src/app/main.py
    ```

## Usage

1.  **Enter a character description:**
    -   Provide a detailed description of the character you want to analyze.
2.  **Generate a profile:**
    -   Click the "Generate Profile" button to have the Gemini API generate a clinical profile.
3.  **View the profile:**
    -   The generated profile will be displayed, including a summary of the character's likely DSM-5 diagnosis, a confidence score, and a detailed explanation.

## Deployment

This application can be deployed to Google Cloud Run using the provided `cloudbuild.yaml` file.

### Prerequisites

1.  **Enable Google Cloud services:**

    ```
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable secretmanager.googleapis.com
    gcloud services enable artifactregistry.googleapis.com
    ```

2.  **Create a secret for your Google API key:**

    ```
    echo -n "YOUR_API_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=-
    ```

3.  **Create an Artifact Registry repository:**

    ```
    gcloud artifacts repositories create app-repo --repository-format=docker --location=us-central1
    ```

### Deploy

```
gcloud builds submit --config cloudbuild.yaml .
```
