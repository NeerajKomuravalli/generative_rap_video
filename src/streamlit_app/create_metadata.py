import requests
from typing import Tuple

import streamlit as st


def create_metadata(audio_file, bpm) -> Tuple[bool, str]:
    # Create meta data
    url = f"http://localhost:8000/create_metadata/{st.session_state.project_name}"
    # Define the data to be sent to the endpoint
    data = {
        "audio_name": audio_file.name,
        "bpm": bpm,
    }

    # Send a POST request to the endpoint
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        if response.json()["success"] is False:
            error = response.json()["error"]
            return False, f"Failed to create metadata with {error}"
    else:
        return (
            False,
            f"Failed to create metadata with status code {response.status_code}",
        )

    return True, None
