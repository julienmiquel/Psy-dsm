"""
Batch processing script for generating character profiles.
"""
import argparse
import json
from dotenv import load_dotenv

from app.services import generate_character_profile

def batch_process(input_file: str, output_file: str, model_id: str):
    """
    Processes character descriptions from an input file and writes the generated
    profiles to an output file.
    """

    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        # Assuming the input file contains one description for simplicity based on previous code,
        # or we read all lines. The previous code joined all lines.
        # Let's keep the logic but fix encoding and linting.
        description = ". ".join(f_in.readlines()).strip()

        print(f"Processing description: {description[:50]}...")
        try:
            profile = generate_character_profile(description, model_id)
            f_out.write(profile.model_dump_json(indent=2))
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"Error processing description: {description[:50]}... Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Batch process character descriptions.")
    parser.add_argument(
        "input_file",
        help="Path to the input file containing character descriptions."
    )
    parser.add_argument(
        "output_file",
        help="Path to the output file to store the generated profiles."
    )
    parser.add_argument(
        "--model_id",
        default="gemini-2.5-pro",
        help="The model to use for generation."
    )
    args = parser.parse_args()

    batch_process(args.input_file, args.output_file, args.model_id)
