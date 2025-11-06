"""
This module provides functions for comparing different types of character profiles
(e.g., CharacterProfile, CHCModel) and generating structured diffs.
"""

import difflib
from typing import Dict, Any
from app.models import CharacterProfile
from app.chc_models import CHCModel

def compare_strings(str1: str, str2: str) -> str:
    """Generates a simple text diff."""
    if not str1: str1 = ""
    if not str2: str2 = ""

    diff = difflib.unified_diff(
        str1.splitlines(keepends=True),
        str2.splitlines(keepends=True),
        fromfile='version 1',
        tofile='version 2',
    )
    return "".join(diff)

def compare_character_profiles(profile1: CharacterProfile, profile2: CharacterProfile) -> Dict[str, Any]:
    """
    Compares two character profiles and returns a structured comparison result.
    """
    comparison = {}

    # Compare summary
    comparison['summary_diff'] = compare_strings(
        profile1.overall_assessment_summary,
        profile2.overall_assessment_summary
    )

    # Compare Holland scores
    p1_scores = {score.theme: score.score for score in profile1.holland_code_assessment.riasec_scores}
    p2_scores = {score.theme: score.score for score in profile2.holland_code_assessment.riasec_scores}
    themes = sorted(list(p1_scores.keys()))
    holland_comparison = []
    for theme in themes:
        score1 = p1_scores.get(theme, 0)
        score2 = p2_scores.get(theme, 0)
        holland_comparison.append({
            "theme": theme,
            "score1": score1,
            "score2": score2,
            "difference": score2 - score1
        })
    comparison['holland_comparison'] = holland_comparison

    # Compare Diagnoses
    p1_diagnoses = {diag.disorder_name: diag for diag in profile1.diagnoses}
    p2_diagnoses = {diag.disorder_name: diag for diag in profile2.diagnoses}

    added_diagnoses = [p2_diagnoses[name].model_dump() for name in p2_diagnoses if name not in p1_diagnoses]
    removed_diagnoses = [p1_diagnoses[name].model_dump() for name in p1_diagnoses if name not in p2_diagnoses]

    modified_diagnoses = []
    common_diagnoses_names = [name for name in p1_diagnoses if name in p2_diagnoses]
    for name in common_diagnoses_names:
        diag1 = p1_diagnoses[name]
        diag2 = p2_diagnoses[name]
        if diag1.model_dump() != diag2.model_dump():
            modified_diagnoses.append({
                "disorder_name": name,
                "profile1": diag1.model_dump(),
                "profile2": diag2.model_dump(),
            })

    comparison['diagnoses_comparison'] = {
        "added": added_diagnoses,
        "removed": removed_diagnoses,
        "modified": modified_diagnoses,
        "common": [p1_diagnoses[name].model_dump() for name in common_diagnoses_names]
    }

    return comparison

def compare_chc_profiles(profile1: CHCModel, profile2: CHCModel) -> Dict[str, Any]:
    """
    Compares two CHC profiles and returns a structured comparison result.
    """
    comparison = {}

    # Compare g-factor
    g_factor1 = profile1.g_factor or 0
    g_factor2 = profile2.g_factor or 0
    comparison['g_factor_comparison'] = {
        "score1": g_factor1,
        "score2": g_factor2,
        "difference": g_factor2 - g_factor1
    }

    # Compare broad abilities
    p1_broad = {ability.id: ability for ability in profile1.broad_abilities}
    p2_broad = {ability.id: ability for ability in profile2.broad_abilities}
    all_broad_ids = sorted(list(set(p1_broad.keys()) | set(p2_broad.keys())))

    broad_ability_comparison = []
    for bid in all_broad_ids:
        ability1 = p1_broad.get(bid)
        ability2 = p2_broad.get(bid)

        score1 = ability1.score if ability1 and ability1.score is not None else 0
        score2 = ability2.score if ability2 and ability2.score is not None else 0

        narrow_comparison = []
        if ability1 and ability2:
            p1_narrow = {n_ability.id: n_ability for n_ability in ability1.narrow_abilities}
            p2_narrow = {n_ability.id: n_ability for n_ability in ability2.narrow_abilities}
            all_narrow_ids = sorted(list(set(p1_narrow.keys()) | set(p2_narrow.keys())))

            for nid in all_narrow_ids:
                n_ability1 = p1_narrow.get(nid)
                n_ability2 = p2_narrow.get(nid)
                n_score1 = n_ability1.score if n_ability1 and n_ability1.score is not None else 0
                n_score2 = n_ability2.score if n_ability2 and n_ability2.score is not None else 0
                narrow_comparison.append({
                    "id": nid,
                    "name": n_ability1.name if n_ability1 else n_ability2.name,
                    "score1": n_score1,
                    "score2": n_score2,
                    "difference": n_score2 - n_score1
                })

        broad_ability_comparison.append({
            "id": bid,
            "name": ability1.name if ability1 else ability2.name,
            "score1": score1,
            "score2": score2,
            "difference": score2 - score1,
            "narrow_abilities": narrow_comparison
        })

    comparison['broad_abilities_comparison'] = broad_ability_comparison
    return comparison
