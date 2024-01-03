import requests

import streamlit as st

from streamlit_app.generate_prompt import generate_prompt
from streamlit_app.generate_image import generate_image
from streamlit_app.generate_video import generate_video
from streamlit_app.project_status import get_project_status


def run_all():
    if st.button("Generate Video"):
        success, message = generate_prompt()
        if not success:
            st.error(message)
            return

        success, data = get_project_status(st.session_state.project_name)
        if success:
            st.session_state.project_status = data
        else:
            st.error(data)

        success, message = generate_image()
        if not success:
            st.error(message)
            return

        success, data = get_project_status(st.session_state.project_name)
        if success:
            st.session_state.project_status = data
        else:
            st.error(data)

        success, message = generate_video()
        if not success:
            st.error(message)
            return

        success, data = get_project_status(st.session_state.project_name)
        if success:
            st.session_state.project_status = data
        else:
            st.error(data)
