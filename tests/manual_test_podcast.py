
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())
# Also add src to path if needed for imports to work correctly from root
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.app.models import CharacterProfile, Module, Activity, HollandCodeAssessment, OceanAssessment
from src.app.services import generate_module_podcast_script
from src.app.logging_config import setup_logging
import logging

# Setup logging to see our new logs
setup_logging()
logger = logging.getLogger(__name__)

def run_test():
    print("--- Starting Podcast Generation Test ---")
    
    # Create minimal valid objects
    # We need to respect the schema for profile and module
    
    profile = CharacterProfile(
        character_name="Jean Test",
        profile_date="2025-10-27",
        overall_assessment_summary="Sujet test présentant une anxiété sociale légère.",
        holland_code_assessment=HollandCodeAssessment(
            riasec_scores=[], 
            top_themes=["Social"], 
            summary="Intérêt pour les autres."
        ),
        ocean_assessment=OceanAssessment(
            ocean_scores=[], 
            summary="Ouverture moyenne, Conscience élevée."
        ),
        diagnoses=[]
    )
    
    module = Module(
        title="Gestion de l'anxiété",
        objective="Apprendre à gérer les montées de stress.",
        session_range="Semaines 1-2",
        activities=[
            Activity(
                title="Respiration carrée",
                details=["Inspirer 4s", "Retenir 4s", "Expirer 4s", "Retenir 4s"]
            )
        ]
    )
    
    model_id = "gemini-2.5-pro"
    
    print(f"Generating podcast for module: {module.title}")
    try:
        script = generate_module_podcast_script(profile, module, model_id)
        
        if script:
            print("\n✅ Generation SUCCESS!")
            print(f"Title: {script.title}")
            print(f"Target Audience: {script.target_audience}")
            print(f"Segments: {len(script.segments)}")
        else:
            print("\n❌ Generation FAILED (Returned None).")
            print("Check logs/app.log or console for 'Generation failed' details.")
            
    except Exception as e:
        print(f"\n❌ Generation ERROR: {e}")
        logger.exception("Test failed with exception")

if __name__ == "__main__":
    run_test()
