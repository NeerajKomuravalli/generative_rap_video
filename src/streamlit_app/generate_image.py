import requests
from typing import Tuple

import streamlit as st

from streamlit_app.project_status import get_project_status


def generate_image() -> Tuple[bool, str]:
    # Define the URL of the endpoint
    url = "http://localhost:8000/stable_diffusion"

    # Define the data to be sent to the endpoint
    data = {
        "project_name": st.session_state.project_name,
    }

    params = {
        "style": st.session_state.stable_diffussion_style,
    }
    # Send a POST request to the endpoint
    response = requests.post(url, data=data, params=params)

    # Check the response
    if response.status_code == 200 and response.json()["success"] is True:
        st.session_state.image_generation_completion = True
    else:
        if response.status_code == 200:
            return (
                False,
                f"Failed to start stable diffusion with error : {response.json()['error']}",
            )
        else:
            return (
                False,
                f"Failed to start stable diffusion with status code : {response.status_code}",
            )

    success, data = get_project_status(st.session_state.project_name)
    if success:
        st.session_state.project_status = data

        return success, None

    return success, data
