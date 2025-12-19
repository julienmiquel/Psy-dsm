# How to Run the Analysis

## Option 1: User Interface (Streamlit)
The easiest way to use the tool.

1.  **Start the Server**:
    ```bash
    poetry run streamlit run src/app/main.py
    ```
2.  **Navigate**: Go to the local URL (usually `http://localhost:8501`).
3.  **Input**:
    *   Paste the character/person text in the text area.
    *   Select the model (Flash for speed, Pro for depth).
    *   Click "Generate Profile".
4.  **Result**: The JSON is parsed and displayed as a readable report with charts (for RIASEC).

## Option 2: Batch Processing
For analyzing a large list of descriptions automatically.

1.  **Prepare Input**: Create a text file `characters.txt` with one description per line.
2.  **Run Script**:
    ```bash
    poetry run python src/app/batch.py characters.txt profiles.json
    ```
3.  **Output**: `profiles.json` will contain a list of all generated `CharacterProfile` objects.

## Option 3: Python API (Replication in Code)
To use the analysis in your own script:

```python
import os
from app.services import generate_character_profile

# Ensure env vars are set
# os.environ["GOOGLE_API_KEY"] = "..."
# os.environ["GOOGLE_CLOUD_PROJECT"] = "..."

description = "Patient is a 30-year-old male presenting with low energy..."
user_id = "manual_run"
model_id = "gemini-2.5-flash"

# Run Analysis
profile = generate_character_profile(description, model_id, user_id)

# Access Data
print(f"Name: {profile.character_name}")
for diagnosis in profile.diagnoses:
    print(f"- {diagnosis.disorder_name}: {diagnosis.dsm_code}")
```
