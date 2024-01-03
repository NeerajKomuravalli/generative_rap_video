import requests

import streamlit as st


def generate_prompt():
    # Define the URL of the endpoint
    url = "http://localhost:8000/generate_prompts"

    # Define the data to be sent to the endpoint
    data = {
        "project_name": st.session_state.project_name,
    }

    # Send a POST request to the endpoint
    response = requests.post(url, data=data)

    # Check the response
    if response.status_code == 200 and response.json()["success"] is True:
        st.session_state.prompt_generation_completion = True
        return True, "Prompts generated successfully!"
    else:
        if response.status_code == 200:
            return (
                False,
                f"Failed to generate prompts with error : {response.json()['error']}",
            )
        else:
            return (
                False,
                f"Failed to generate prompts with status code : {response.status_code}",
            )
