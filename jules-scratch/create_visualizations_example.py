
from src.app.models import HollandCode, HollandCodeAssessment
from src.app.visualizations import create_riasec_visualizations

def main():
    """Creates a sample RIASEC assessment and generates visualizations."""
    sample_scores = [
        HollandCode(theme="Realistic", score=8, description="Practical, hands-on, and tool-oriented."),
        HollandCode(theme="Investigative", score=7, description="Analytical, intellectual, and scientific."),
        HollandCode(theme="Artistic", score=9, description="Creative, original, and independent."),
        HollandCode(theme="Social", score=4, description="Cooperative, supportive, and helping others."),
        HollandCode(theme="Enterprising", score=6, description="Persuasive, energetic, and status-oriented."),
        HollandCode(theme="Conventional", score=5, description="Organized, detail-oriented, and conforming.")
    ]

    assessment = HollandCodeAssessment(
        riasec_scores=sample_scores,
        top_themes=["Artistic", "Realistic", "Investigative"],
        summary="This individual shows a strong inclination towards creative and practical pursuits."
    )

    create_riasec_visualizations(assessment)

if __name__ == "__main__":
    main()
