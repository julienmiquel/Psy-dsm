
import matplotlib.pyplot as plt
import numpy as np
import os
from .models import HollandCodeAssessment

def create_riasec_visualizations(assessment: HollandCodeAssessment, output_dir: str = "output"):
    """
    Generates and saves a bar chart and a radar chart for the given RIASEC assessment.

    Args:
        assessment: The HollandCodeAssessment object containing the RIASEC scores.
        output_dir: The directory to save the generated charts. Defaults to "output".
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    labels = [score.theme for score in assessment.riasec_scores]
    values = [score.score for score in assessment.riasec_scores]
    
    # Bar Chart
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color=['#FF4136', '#FFDC00', '#0074D9', '#2ECC40', '#FF851B', '#B10DC9'])
    plt.title('RIASEC Scores')
    plt.xlabel('Theme')
    plt.ylabel('Score')
    plt.grid(axis='y', linestyle='--')
    bar_chart_path = os.path.join(output_dir, 'riasec_bar_chart.png')
    plt.savefig(bar_chart_path)
    plt.close()

    # Radar Chart
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='red', alpha=0.25)
    ax.plot(angles, values, color='red', linewidth=2)
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    plt.title('RIASEC Profile', size=20, color='red', y=1.1)
    radar_chart_path = os.path.join(output_dir, 'riasec_radar_chart.png')
    plt.savefig(radar_chart_path)
    plt.close()

    print(f"Charts saved to {os.path.abspath(output_dir)}")


def get_riasec_figures(assessment: HollandCodeAssessment):
    """
    Generates a bar chart and a radar chart for the given RIASEC assessment and returns the figures.

    Args:
        assessment: The HollandCodeAssessment object containing the RIASEC scores.

    Returns:
        A tuple containing the bar chart and radar chart matplotlib figures.
    """
    if assessment is None:
        return None, None
    labels = [score.theme for score in assessment.riasec_scores]
    values = [score.score for score in assessment.riasec_scores]
    
    # Bar Chart
    bar_fig, bar_ax = plt.subplots(figsize=(10, 6))
    bar_ax.bar(labels, values, color=['#FF4136', '#FFDC00', '#0074D9', '#2ECC40', '#FF851B', '#B10DC9'])
    bar_ax.set_title('RIASEC Scores')
    bar_ax.set_xlabel('Theme')
    bar_ax.set_ylabel('Score')
    bar_ax.grid(axis='y', linestyle='--')

    # Radar Chart
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    radar_values = values + values[:1]
    radar_angles = angles + angles[:1]

    radar_fig, radar_ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    radar_ax.fill(radar_angles, radar_values, color='red', alpha=0.25)
    radar_ax.plot(radar_angles, radar_values, color='red', linewidth=2)
    
    radar_ax.set_yticklabels([])
    radar_ax.set_xticks(angles)
    radar_ax.set_xticklabels(labels)

    radar_ax.set_title('RIASEC Profile', size=20, color='red', y=1.1)

    return bar_fig, radar_fig
