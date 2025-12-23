"""
This module provides the dashboard UI for displaying character profiles.
"""
import streamlit as st
from app.models import CharacterProfile
from app.visualizations import get_riasec_figures

def display_holland_assessment(profile: CharacterProfile):
    """Renders the Holland Code Assessment section."""
    holland_assessment = profile.holland_code_assessment
    if not holland_assessment:
        return

    st.subheader("Holland Code (RIASEC) Assessment")
    st.write(f"**Top Themes:** {', '.join(holland_assessment.top_themes)}")
    st.write(f"**Summary:** {holland_assessment.summary}")
    for score in holland_assessment.riasec_scores:
        st.markdown(
            f"- **{score.theme}:** {score.score}/10 - {score.description}"
        )

    bar_chart, radar_chart = get_riasec_figures(holland_assessment)
    col1, col2 = st.columns(2)
    with col1:
        st.header("RIASEC Scores Bar Chart")
        st.pyplot(bar_chart)
    with col2:
        st.header("RIASEC Profile Radar Chart")
        st.pyplot(radar_chart)

    st.markdown("---")
    with st.expander("Full holland assessment JSON"):
        st.json(holland_assessment.model_dump())

def display_diagnoses(profile: CharacterProfile):
    """Displays the diagnostic impressions."""
    diagnoses = profile.diagnoses
    if not diagnoses:
        st.info("No formal diagnoses were assigned.")
    else:
        st.subheader("Diagnostic Impressions")
        for dx in diagnoses:
            # Check if dsm_code is present
            title = f"{dx.disorder_name} ({dx.dsm_code})" if dx.dsm_code else dx.disorder_name
            with st.expander(title):
                st.write(f"**Category:** {dx.dsm_category}")

                if dx.specifiers:
                    st.write("**Specifiers:**")
                    for s in dx.specifiers:
                        st.markdown(f"- {s.specifier_type}: {s.value}")

                st.write("**Criteria Met (Justification):**")
                if dx.criteria_met:
                    for c in dx.criteria_met:
                        st.markdown(f"- {c}")
                else:
                    st.markdown("- None listed.")

                st.write("**Functional Impairment:**")
                st.write(dx.functional_impairment or 'Not specified.')

                if dx.diagnostic_note:
                    st.write("**Notes:**")
                    st.write(dx.diagnostic_note)
        st.markdown("---")
        with st.expander("Full diagnoses JSON"):
            st.json([d.model_dump() for d in diagnoses])

def display_profile(profile: CharacterProfile):
    """Renders the character profile in the UI."""
    profile_dict = profile.model_dump()

    st.header("Generated Clinical Profile")
    st.subheader(f"Character: {profile_dict.get('character_name', 'N/A')}")
    st.caption(f"Profile Date: {profile_dict.get('profile_date', 'N/A')}")

    st.markdown("---")

    st.subheader("Overall Assessment")
    summary = profile_dict.get('overall_assessment_summary', 'No summary provided.')
    st.write(summary)

    display_holland_assessment(profile)
    display_diagnoses(profile)
