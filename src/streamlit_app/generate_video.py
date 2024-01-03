import requests

import streamlit as st


def generate_video():
    url = "http://localhost:8000/generate_video"
    data = {
        "project_name": st.session_state.project_name,
    }

    response = requests.post(url, data=data)

    if response.status_code == 200 and response.json()["success"] is True:
        return True, "Video generated successfully!"
    else:
        if response.status_code == 200:
            return (
                False,
                f"Failed to generate video with error : {response.json()['error']}",
            )
        else:
            return (
                False,
                f"Failed to generate video with status code : {response.status_code}",
            )
