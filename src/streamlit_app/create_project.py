import requests
from typing import Tuple, Union

import streamlit as st

from streamlit_app.project_status import get_project_status


def create_project() -> Tuple[bool, str]:
    # Define the URL of the endpoint
    url = f"http://localhost:8000/create_project/{st.session_state.project_name}"

    # Send a POST request to the endpoint
    response = requests.post(url)

    # Check the response
    if response.status_code == 200:
        if response.json()["success"] is True:
            pass
            # st.success("Project created successfully!")
        else:
            error = response.json()["error"]
            return False, f"Failed to create project with {error}"
    else:
        return (
            False,
            f"Failed to create project with status code {response.status_code}",
        )

    success, data = get_project_status(st.session_state.project_name)
    if success:
        st.session_state.project_status = data

        return success, None

    return success, data
