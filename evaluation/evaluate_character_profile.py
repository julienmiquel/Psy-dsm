# -*- coding: utf-8 -*-
"""
This script evaluates the 'generate_character_profile' function
using the Vertex AI Gen AI Evaluation Service.

To run this script, you might need to install the evaluation library:
pip install "google-cloud-aiplatform[evaluation]"
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from vertexai import Client

from vertexai.generative_models._evaluations import EvaluationDataset

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app.services import generate_character_profile
from src.app.models import CharacterProfile

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Main function to run the evaluation.
    """
    # @title ### Set Google Cloud project information
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    client = Client(project=PROJECT_ID, location=LOCATION)

    # @title ### Prepare Evaluation Dataset
    # Using prompts that would test the generate_character_profile function
    eval_df = pd.DataFrame({
        "prompt": [
            "Subject is a 52-year-old male architect. He reports chronic feelings of emptiness and instability in his interpersonal relationships, self-image, and emotions. He has a history of intense and unstable relationships, marked by alternating between extremes of idealization and devaluation. He describes frantic efforts to avoid real or imagined abandonment. He also reports recurrent suicidal ideation and gestures, as well as chronic feelings of emptiness.",
            "A 30-year-old software engineer who is extremely meticulous, orderly, and preoccupied with details, rules, and lists. Their focus on perfectionism interferes with task completion. They are excessively devoted to work to the exclusion of leisure activities and friendships. They are overconscientious and inflexible about matters of morality and ethics.",
            "A 25-year-old graduate student who has been feeling down for over a month. They have lost interest in their studies and hobbies, feel tired all the time, and have trouble sleeping. They report feelings of worthlessness and have difficulty concentrating. They have started to miss classes and withdraw from friends.",
            "A 40-year-old woman with no history of mental illness. She is generally happy, has a stable job, a good social network, and enjoys her life. She reports no significant distress or impairment in her daily functioning.",
        ]
    })

    # @title ### Generate Responses
    # We are generating the responses from our custom function
    model_id = "gemini-2.5-flash" # Using a recent model
    responses = []
    print("Generating responses...")
    for i, prompt in enumerate(eval_df["prompt"]):
        print(f"Processing prompt {i+1}/{len(eval_df['prompt'])}")
        try:
            profile: CharacterProfile = generate_character_profile(description=prompt, model_id=model_id)
            responses.append(profile.model_dump_json(indent=2))
        except Exception as e:
            error_message = f"Error generating profile for prompt: {prompt}\n{e}"
            print(error_message)
            responses.append(f"Error: {e}") # Append error message to see it in the results

    eval_df["response"] = responses

    print("--- Generated Responses ---")
    print(eval_df)
    print("---------------------------")


    # We pass the dataframe with prompts and our generated responses to run_inference.
    # This will create the EvaluationDataset object for us.
    print("Creating evaluation dataset...")
    eval_dataset = EvaluationDataset(eval_dataset_df=eval_df)

    # @title ### Run Evaluation
    # Evaluate the responses using the GENERAL_QUALITY adaptive rubric-based metric by default.
    print("Running evaluation...")
    eval_result = client.evals.evaluate(dataset=eval_dataset)

    print("--- Evaluation Result ---")
    print(eval_result)
    print("-------------------------")

if __name__ == "__main__":
    main()
