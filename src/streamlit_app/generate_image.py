import requests

import streamlit as st


def generate_image():
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
        return True, "Stable diffusion started successfully!"
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
