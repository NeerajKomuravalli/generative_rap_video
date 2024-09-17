import requests
import streamlit as st

from streamlit_app.project_status import get_project_status


def handle_project_tab():
    # Audio files uploader
    with st.form(key="my_form"):
        project_name = st.text_input("Enter the project name")
        submit_button = st.form_submit_button(label="Submit")
        if submit_button:
            st.session_state.project_name_state = True
            st.session_state.project_name = project_name

            # Define the URL of the endpoint
            url = f"http://localhost:8000/create_project/{project_name}"

            # Send a POST request to the endpoint
            response = requests.post(url)

            # Check the response
            if response.status_code == 200:
                if response.json()["success"] is True:
                    st.success("Project created successfully!")
                else:
                    error = response.json()["error"]
                    st.error(f"Failed to create project with {error}")
            else:
                st.error(
                    f"Failed to create project with status code {response.status_code}"
                )

            success, data = get_project_status(project_name)
            if success:
                st.session_state.project_status = data
            else:
                st.error(data)
