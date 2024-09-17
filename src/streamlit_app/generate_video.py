import requests
from typing import Tuple

import streamlit as st

from streamlit_app.project_status import get_project_status


def generate_video():
    url = "http://localhost:8000/generate_video"
    data = {
        "project_name": st.session_state.project_name,
    }

    response = requests.post(url, data=data)

    if response.status_code == 200 and response.json()["success"] is False:
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

    success, data = get_project_status(st.session_state.project_name)
    if success:
        st.session_state.project_status = data

        return success, None

    return success, data
