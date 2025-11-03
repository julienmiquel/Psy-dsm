import streamlit as st
from app.database import db_service
from app.user_models import UserProfile

def crm_page():
    st.title("User Profile")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("You need to be logged in to view this page.")
        return

    user_profile = db_service.get_user_profile(user_id)
    if not user_profile:
        user_profile = UserProfile(user_id=user_id)

    with st.form("user_profile_form"):
        st.write("Edit your profile:")
        name = st.text_input("Name", value=user_profile.name)
        surname = st.text_input("Surname", value=user_profile.surname)
        email = st.text_input("Email", value=user_profile.email)
        
        submitted = st.form_submit_button("Save")
        if submitted:
            user_profile.name = name
            user_profile.surname = surname
            user_profile.email = email
            db_service.save_user_profile(user_profile)
            st.success("Profile saved!")
            st.rerun()

    st.write("---")
    st.write("Current Profile:")
    st.write(f"**Name:** {user_profile.name}")
    st.write(f"**Surname:** {user_profile.surname}")
    st.write(f"**Email:** {user_profile.email}")
