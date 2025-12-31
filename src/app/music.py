
"""
Handles the generation of music using Google's Lyria model.

This module provides a client class for interacting with the Vertex AI endpoint
for the Lyria music generation model. It handles authentication, request
formatting, and saving the generated audio.
"""
import logging
import os
import requests
import google.auth
import google.auth.transport.requests
from tenacity import before_sleep_log, retry, stop_after_delay, wait_exponential

from app.utils import save_base64_audio
# from src.core import config # Removed as we use env vars directly or simplified config

logger = logging.getLogger(__name__)

class MusicGenerator:
    """
    A client for generating music using Google's Lyria model via Vertex AI.

    This class encapsulates the logic for authenticating with Google Cloud,
    sending requests to the Lyria model endpoint, and handling the responses.
    """

    def __init__(self):
        """
        Initializes the MusicGenerator.
        """
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("MODEL_LYRIA_LOCATION", "us-central1")
        self.model_id = "lyria-002" # Hardcoded based on request or env
        
        if not self.project_id:
            logger.warning("GOOGLE_CLOUD_PROJECT env var not set. Attempting to fetch from default credentials...")
            try:
                _, self.project_id = google.auth.default()
                logger.info(f"Retrieved project ID from credentials: {self.project_id}")
            except Exception as e:
                logger.error(f"Failed to retrieve project ID from credentials: {e}")

        if not self.project_id:
             logger.error("Project ID is missing. Music generation will fail.")

        self.api_endpoint = (
            f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}"
            f"/locations/{self.location}/publishers/google/models/{self.model_id}:predict"
        )
        self.access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        """
        Refreshes and returns the default gcloud access token.

        Returns:
            A valid Google Cloud access token.

        Raises:
            Exception: If token generation fails.
        """
        try:
            creds, _ = google.auth.default()
            auth_req = google.auth.transport.requests.Request()
            creds.refresh(auth_req)
            return creds.token
        except Exception as e:
            logger.error(f"Failed to get gcloud auth token: {e}")
            raise

    # @retry(
    #     wait=wait_exponential(multiplier=2, min=5, max=10),
    #     stop=stop_after_delay(300),  # 5 minutes
    #     before_sleep=before_sleep_log(logging, logging.WARNING),
    #     reraise=True
    # )
    def _send_prediction_request(self, request_data: dict) -> dict:
        """
        Sends a prediction request to the Lyria model endpoint with retry logic.

        Args:
            request_data: The data to be sent in the request body.

        Returns:
            The JSON response from the API.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {"instances": [request_data], "parameters": {}}
        # Note: 5 min timeout for music generation is reasonable
        response = requests.post(self.api_endpoint, headers=headers, json=payload, timeout=300) 
        response.raise_for_status()
        return response.json()

    @retry(
        wait=wait_exponential(multiplier=2, min=5, max=60),
        stop=stop_after_delay(400),  
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def generate_and_save(
        self,
        prompt: str,
        output_path: str,
        negative_prompt: str = "",
        duration_seconds: int = 30
    ):
        """
        Generates music from a prompt and saves it to a file.

        If the output file already exists, the generation is skipped.

        Args:
            prompt: The text prompt to guide the music generation.
            output_path: The path to save the generated WAV file.
            negative_prompt: A text prompt of what to avoid in the music.
            duration_seconds: The desired duration of the music in seconds.
        """
        if os.path.exists(output_path):
            logger.info(f"Music file {output_path} already exists. Skipping.")
            return

        try:
            logger.info(f"Generating {duration_seconds}s of music for prompt: '{prompt}'")
            request_data = {
                "prompt": prompt,
                "negativePrompt": negative_prompt,
                "durationSeconds": duration_seconds, 
            }
            # Note: Lyria usage might require durationSeconds to be omitted or 
            # specific values depending on the specific model version constraints.
            # User snippet had it commented out, but function arg has it.
            # We will try sending it.
            
            response = self._send_prediction_request(request_data)

            if "predictions" in response and response["predictions"]:
                base64_audio = response["predictions"][0].get("bytesBase64Encoded")
                if base64_audio:
                    save_base64_audio(base64_audio, output_path)
                    logger.info(f"Music saved successfully to {output_path}")
                else:
                    logger.error("API response missing 'bytesBase64Encoded' field.")
            else:
                logger.error(f"Music generation failed. API response: {response}")

        except Exception as e:
            logger.warning(f"An error occurred during music generation: {e}")
            if len(prompt) > 10:
                short_prompt = prompt[:int(len(prompt)*0.8)]
                logger.warning(f"Retrying with a shorter prompt: {short_prompt}")
                # Use self to retry recursively (though tenacity handles retries, this is a logic retry)
                # Ideally, we should let the caller handle prompt adjustment or use a different retry strategy
                # For now, simplistic recursion is okay but risking infinite loop if logic flaw.
                # Let's rely on tenacity for network errors and log for logic errors.
                # The user code had this logic. We'll keep it but be careful.
                # actually, user code recurses.
                self.generate_and_save(short_prompt, output_path, negative_prompt, duration_seconds)
            else:
                logger.error(f"Given up on music generation for prompt: '{prompt}'")
