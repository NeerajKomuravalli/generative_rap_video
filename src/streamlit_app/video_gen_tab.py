import requests
import streamlit as st


def handle_video_gen_tab():
    if st.button("Generate Video"):
        url = "http://localhost:8000/generate_video"
        data = {
            "project_name": st.session_state.project_name,
        }

        response = requests.post(url, data=data)

        if response.status_code == 200 and response.json()["success"] is True:
            st.success("Video generated successfully!")
        else:
            st.write(response.json()["error"])
            st.error("Failed to generate video.")
