"""
This module provides functionality for batch processing of character descriptions.
"""
import argparse
from dotenv import load_dotenv

from app.services import generate_character_profile

def batch_process(input_file: str, output_file: str, model_id: str):
    """
    Processes character descriptions from an input file and writes the generated
    profiles to an output file as a JSON array.
    """

    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:

        f_out.write("[\n")
        first = True

        for line in f_in:
            description = line.strip()
            if not description:
                continue

            print(f"Processing description: {description[:50]}...")
            try:
                profile = generate_character_profile(description, model_id)
                if not first:
                    f_out.write(",\n")
                f_out.write(profile.model_dump_json(indent=2))
                first = False
            except Exception as e: # pylint: disable=broad-exception-caught
                print(f"Error processing description: {description[:50]}... Error: {e}")

        f_out.write("\n]")
if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Batch process character descriptions.")
    parser.add_argument(
        "input_file",
        help="Path to the input file containing character descriptions (one per line)."
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
