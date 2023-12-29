import requests
import streamlit as st


def update_metadata(project_name: str):
    # Create meta data
    url = f"http://localhost:8000/update_metadata/{project_name}"

    # Send a POST request to the endpoint
    response = requests.post(url)

    # Check the response
    if response.status_code == 200:
        if response.json()["success"] is True:
            st.success("Metadata updated successfully!")
        else:
            error = response.json()["error"]
            st.error(f"Failed to update metadata with {error}")
    else:
        st.error(f"Failed to update metadata with status code {response.status_code}")
