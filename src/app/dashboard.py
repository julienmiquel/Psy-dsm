import streamlit as st
from app.models import CharacterProfile
from app.visualizations import get_riasec_figures

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

    # Display Holland Code Assessment
    holland_assessment = profile_dict.get('holland_code_assessment')
    if holland_assessment:
        st.subheader("Holland Code (RIASEC) Assessment")
        st.write(f"**Top Themes:** {', '.join(holland_assessment.get('top_themes', []))}")
        st.write(f"**Summary:** {holland_assessment.get('summary', 'No summary provided.')}")
        for score in holland_assessment.get('riasec_scores', []):
            st.markdown(f"- **{score.get('theme')}:** {score.get('score')}/10 - {score.get('description')}")

        bar_chart, radar_chart = get_riasec_figures(profile.holland_code_assessment)
        col1 , col2 = st.columns(2)
        with col1:
            st.header("RIASEC Scores Bar Chart")
            st.pyplot(bar_chart)
        with col2:
            st.header("RIASEC Profile Radar Chart")
            st.pyplot(radar_chart)
        # st.header("RIASEC Scores Bar Chart")
        # st.pyplot(bar_chart)

        # st.header("RIASEC Profile Radar Chart")
        # st.pyplot(radar_chart)
        st.markdown("---")
        with st.expander("Full holland assessment JSON"):
            st.json(holland_assessment)

    diagnoses = profile_dict.get('diagnoses', [])
    if not diagnoses:
        st.info("No formal diagnoses were assigned.")
    else:
        st.subheader("Diagnostic Impressions")
        for dx in diagnoses:
            with st.expander(f"{dx.get('disorder_name', 'N/A')} ({dx.get('dsm_code', 'N/A')})"):
                st.write(f"**Category:** {dx.get('dsm_category', 'N/A')}")

                specifiers = dx.get('specifiers', [])
                if specifiers:
                    st.write("**Specifiers:**")
                    for s in specifiers:
                        st.markdown(f"- {s.get('specifier_type')}: {s.get('value')}")

                st.write("**Criteria Met (Justification):**")
                criteria = dx.get('criteria_met', [])
                if criteria:
                    for c in criteria:
                        st.markdown(f"- {c}")
                else:
                    st.markdown("- None listed.")

                st.write("**Functional Impairment:**")
                impairment = dx.get('functional_impairment', 'Not specified.')
                st.write(impairment)

                note = dx.get('diagnostic_note')
                if note:
                    st.write("**Notes:**")
                    st.write(note)
        st.markdown("---")
        with st.expander("Full diagnoses JSON"):
            st.json(diagnoses)