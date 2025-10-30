import json
from app.models import CharacterProfile, TCCProgram

if __name__ == "__main__":
    schema = CharacterProfile.model_json_schema()
    with open("CharacterProfile_schema.json", "w") as f:
        json.dump(schema, f, indent=2)

    schema = TCCProgram.model_json_schema()
    with open("tcc_program_schema.json", "w") as f:
        json.dump(schema, f, indent=2)