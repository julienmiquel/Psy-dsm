import pytest
import matplotlib.pyplot as plt
from src.app.models import HollandCode, HollandCodeAssessment
from src.app.visualizations import get_riasec_figures

def test_get_riasec_figures():
    """
    Tests the get_riasec_figures function to ensure it returns valid matplotlib figures.
    """
    # Sample Data
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

    bar_chart, radar_chart = get_riasec_figures(assessment)

    # Check if the returned objects are figures
    assert isinstance(bar_chart, plt.Figure)
    assert isinstance(radar_chart, plt.Figure)

    # Check the titles of the figures
    assert bar_chart.axes[0].get_title() == 'RIASEC Scores'
    assert radar_chart.axes[0].get_title() == 'RIASEC Profile'

    # Check if the figures can be closed without errors
    plt.close(bar_chart)
    plt.close(radar_chart)
