import requests
import streamlit as st

from streamlit_app.generate_video import generate_video


def handle_video_gen_tab():
    if st.button("Generate Video"):
        succcess, message = generate_video()
        if not succcess:
            st.error(message)

    if st.session_state.project_status.video != "":
        st.video(st.session_state.project_status.video)
