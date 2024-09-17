import streamlit as st


def display():
    st.video(st.session_state.project_status.video)
