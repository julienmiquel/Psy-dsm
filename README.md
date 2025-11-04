# Psy-dsm
A tool to help to map psychological pathologies based on DSM-5 reference book.

This application uses the Google Gemini API to generate a clinical profile of a fictional character based on a user-provided description. The profile is based on the DSM-5 criteria and is intended for creative and academic purposes.

## Project Structure

- `src/app`: Contains the main application code.
  - `main.py`: The entry point for the Streamlit application.
  - `models.py`: Defines the Pydantic models for the application.
  - `services.py`:  Contains the business logic of the application.
- `terraform`: Contains the Terraform code for infrastructure as code.
  - `main.tf`:  Defines the Google Cloud Run service and other resources.
  - `variables.tf`:  Defines the variables used in the Terraform configuration.
- `tests`: Contains the tests for the application.
- `cloudbuild.yaml`:  Defines the CI/CD pipeline for building and deploying the application.
- `Dockerfile`:  Used to containerize the application.
- `poetry.lock` and `pyproject.toml`:  Defines the project dependencies.

## Data Model

The application uses a set of Pydantic models to represent the data. The core models are:

*   **`CharacterProfile`**: Represents the main clinical profile of a character, including DSM-5 diagnoses and a Holland Code (RIASEC) assessment.
*   **`CHCModel`**: Represents a cognitive profile based on the Cattell-Horn-Carroll (CHC) model.
*   **`TCCProgram`**: Represents a cognitive-behavioral therapy (TCC) program.
*   **`UserProfile`**: Represents a user's profile information.

### Data Linking

The different profiles for a character are linked together using a `character_id`. This ID is a unique identifier for each character.

To provide a more robust and scalable way to manage character data, we use a centralized character index.

#### Centralized Character Index

For local storage, a `character_index.json` file is used to maintain a mapping between a character's PII (Personally Identifiable Information) and their various profiles.

**Structure of `character_index.json`:**
```json
{
  "character_id_123": {
    "pii": { "character_name": "John Doe" },
    "profiles": {
      "character": "local_db/profiles/character_id_123.json",
      "chc": "local_db/chc/character_id_123.json",
      "tcc": "local_db/tcc_programs/character_id_123.json"
    }
  }
}
```

This centralized index provides a single source of truth for all data related to a character, making the system more organized and easier to maintain.

For cloud-based storage (Datastore/Firestore), a similar approach is used with a "CharacterIndex" kind/collection.

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
    poetry run streamlit run src/app/main.py
    ```

## Usage

1.  **Enter a character description:**
    -   Provide a detailed description of the character you want to analyze in the text area.
2.  **Generate a profile:**
    -   Click the "Generate Profile" button to have the Gemini API generate a clinical profile.
3.  **View the profile:**
    -   The generated profile will be displayed below the button, including a summary of the character's likely DSM-5 diagnosis, a Holland Code assessment, and a detailed explanation.

## Batch Processing

This application includes a batch processing mode that allows you to generate profiles for multiple character descriptions from an input file.

### How to Use

1.  **Create an input file:**
    -   Create a text file (e.g., `characters.txt`) with one character description per line.

2.  **Run the batch script:**
    -   Execute the `src/app/batch.py` script from your terminal, providing the input and output file paths as arguments:

    ```
    poetry run python src/app/batch.py characters.txt profiles.json
    ```

3.  **View the output:**
    -   The script will process each description and write the generated profiles to the specified output file (e.g., `profiles.json`) in JSON format.

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
