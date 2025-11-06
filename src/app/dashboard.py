import streamlit as st
from app.chc_models import CHCModel
from app.models import CharacterProfile
from app.visualizations import get_riasec_figures
from app.comparison_service import compare_character_profiles, compare_chc_profiles


def display_chc_profile(profile: CHCModel):
    """Renders the CHC profile in the UI."""
    profile_dict = profile.model_dump()

    st.header("Generated CHC Profile")
    if profile.character_name:
        st.subheader(f"Character: {profile.character_name}")
    if profile.profile_datetime:
        st.write(f"**Profile Datetime:** {profile.profile_datetime}")

    if profile_dict.get('g_factor'):
        st.subheader(f"General Intelligence (g-factor): {profile_dict.get('g_factor')}")

    st.markdown("---")

    st.subheader("Broad Abilities")
    broad_abilities = profile_dict.get('broad_abilities', [])
    if not broad_abilities:
        st.info("No broad abilities were identified.")
    else:
        for ability in broad_abilities:
            with st.expander(f"{ability.get('name')} ({ability.get('id')}) - Score: {ability.get('score', 'N/A')}"):
                st.write(f"**Description:** {ability.get('description', 'N/A')}")
                if ability.get('evidence_summary'):
                    st.write(f"**Evidence Summary:** {ability.get('evidence_summary')}")

                narrow_abilities = ability.get('narrow_abilities', [])
                if narrow_abilities:
                    st.write("**Narrow Abilities:**")
                    for narrow in narrow_abilities:
                        st.markdown(f"- **{narrow.get('name')} ({narrow.get('id')}):** Score: {narrow.get('score', 'N/A')}")
                        st.markdown(f"  - {narrow.get('description', 'N/A')}")
                        if narrow.get('evidence_summary'):
                            st.markdown(f"  - **Evidence Summary:** {narrow.get('evidence_summary')}")
                else:
                    st.write("No narrow abilities identified for this broad ability.")
    
    if profile_dict.get('poor_coverage_topics'):
        st.subheader("Topics with Poor Coverage")
        st.warning("The following topics had poor coverage in the provided text, which may affect the accuracy of the CHC profile:")
        for topic in profile_dict['poor_coverage_topics']:
            st.markdown(f"- {topic}")

    st.markdown("---")
    with st.expander("Full CHC Profile JSON"):
        st.json(profile_dict)

    if profile.raw_text_bloc:
        with st.expander("Raw Text Input"):
            st.text(profile.raw_text_bloc)

def display_comparison(profile1, profile2):
    """Renders the comparison of two profiles."""
    st.header("Profile Comparison")

    if isinstance(profile1, CharacterProfile) and isinstance(profile2, CharacterProfile):
        st.subheader("Comparing Character Profiles (RIASEC)")
        comparison_result = compare_character_profiles(profile1, profile2)

        st.markdown("#### Overall Assessment Summary Diff")
        st.text(comparison_result['summary_diff'])

        st.markdown("#### Holland Code (RIASEC) Score Comparison")
        st.table(comparison_result['holland_comparison'])

        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(get_riasec_figures(profile1.holland_code_assessment)[1])
        with col2:
            st.pyplot(get_riasec_figures(profile2.holland_code_assessment)[1])

    elif isinstance(profile1, CHCModel) and isinstance(profile2, CHCModel):
        st.subheader("Comparing CHC Profiles")
        comparison_result = compare_chc_profiles(profile1, profile2)

        st.markdown("#### General Intelligence (g-factor) Comparison")
        st.table([comparison_result['g_factor_comparison']])

        st.markdown("#### Broad Abilities Comparison")
        st.table(comparison_result['broad_abilities_comparison'])

    else:
        st.error("Profile types are incompatible for comparison.")


def display_hexa3d_assessment(assessment):
    """Renders the Hexa3D assessment in the UI."""
    st.subheader("Hexa3D Assessment")
    st.write(f"**Assessment Datetime:** {assessment.assessment_datetime}")
    st.write(f"**Summary:** {assessment.summary}")

    st.write(f"**Top Themes:** {', '.join(assessment.code_global_top_themes)}")
    st.write(f"**Differentiation:** {assessment.niveau_differenciation_global}")
    st.write(f"**Consistency:** {assessment.niveau_consistance_global}")

    for profile_type in ["profil_activites", "profil_qualites", "profil_professions", "profil_global"]:
        profile_data = getattr(assessment, profile_type)
        with st.expander(f"{profile_type.replace('_', ' ').title()}"):
            st.write(f"**Code RIASEC:** {profile_data.code_riasec}")
            st.write("**Notes Brutes:**")
            st.json(profile_data.notes_brutes.model_dump_json())
            st.write("**Notes Etalonnees:**")
            st.json(profile_data.notes_etalonnees.model_dump_json())

    with st.expander("Dimensions Secondaires"):
        st.json(assessment.dimensions_secondaires.model_dump_json())


def display_profile(profile: CharacterProfile):
    """Renders the character profile in the UI."""
    st.header(f"Character Profile: {profile.character_name}")
    st.write(f"**Profile Datetime:** {profile.profile_datetime}")

    if profile.overall_assessment_summary:
        st.subheader("Overall Assessment Summary")
        st.write(profile.overall_assessment_summary)

    st.subheader("Diagnoses")
    if not profile.diagnoses:
        st.info("No diagnoses were identified.")
    else:
        for diagnosis in profile.diagnoses:
            with st.expander(f"{diagnosis.disorder_name} ({diagnosis.dsm_code})"):
                st.write(f"**DSM Category:** {diagnosis.dsm_category}")
                st.write("**Criteria Met:**")
                for criterion in diagnosis.criteria_met:
                    st.markdown(f"- {criterion}")
                if diagnosis.specifiers:
                    st.write("**Specifiers:**")
                    for specifier in diagnosis.specifiers:
                        st.markdown(f"- {specifier.specifier_type}: {specifier.value}")
                if diagnosis.functional_impairment:
                    st.write(f"**Functional Impairment:** {diagnosis.functional_impairment}")
                if diagnosis.diagnostic_note:
                    st.write(f"**Diagnostic Note:** {diagnosis.diagnostic_note}")

    if profile.holland_code_assessment:
        st.subheader("Holland Code (RIASEC) Assessment")
        assessment = profile.holland_code_assessment
        st.write(f"**Top Themes:** {', '.join(assessment.top_themes)}")
        st.write(f"**Summary:** {assessment.summary}")

        for score in assessment.riasec_scores:
            st.write(f"**{score.theme}:** {score.score} - {score.description}")

        bar_chart, radar_chart = get_riasec_figures(profile.holland_code_assessment)
        col1 , col2 = st.columns(2)
        with col1:
            st.header("RIASEC Scores Bar Chart")
            st.pyplot(bar_chart)
        with col2:
            st.header("RIASEC Profile Radar Chart")
            st.pyplot(radar_chart)
        st.markdown("---")

    if profile.hexa3d_assessment:
        display_hexa3d_assessment(profile.hexa3d_assessment)

    with st.expander("Full Profile JSON"):
        st.json(profile.model_dump())

    if profile.raw_text_bloc:
        with st.expander("Raw Text Input"):
            st.text(profile.raw_text_bloc)