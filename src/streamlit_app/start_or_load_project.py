import requests

import streamlit as st

from streamlit_app.project_status import get_project_status
from streamlit_app.update_meta_data import update_metadata


def start_or_load_project():
    with st.form(key="my_form"):
        project_name = st.text_input("Enter the project name")
        ## audio file
        audio_file = st.file_uploader("Upload your audio file", type=["mp3", "wav"])
        ## bpm
        bpm = st.number_input("Enter the BPM of the track")

        submit_button = st.form_submit_button(label="Submit")

        status_message = st.empty()
        if submit_button:
            if project_name == "":
                st.error("Please enter the project name")

            st.session_state.project_name_state = True
            st.session_state.project_name = project_name

            # Define the URL of the endpoint
            url = f"http://localhost:8000/create_project/{project_name}"

            # Send a POST request to the endpoint
            response = requests.post(url)

            # Check the response
            if response.status_code == 200:
                if response.json()["success"] is True:
                    pass
                    # st.success("Project created successfully!")
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

            if st.session_state.project_status.original != "":
                if audio_file:
                    # This means user has added an audio file but the project already has an audio file
                    # NOTE: As of now we will notify user about this
                    status_message.error("Project already has audio file")
                    return
                if bpm:
                    # No audio file present but bpm given

                    status_message.error(
                        "You have added a BPM for a project with an audio file and bpm"
                    )
                    return
                # If the project already has an audio file and bpm, we don't need to do anything
                status_message.success("Project loaded successfully")
                return
            if not (audio_file and bpm):
                # This means user has not added an audio file or bpm
                status_message.error("Please add an audio file and bpm")
                return

            audio_uploaded = False
            chunks_created = False
            # Create a for status message

            status_message.text("Uploading audio...")
            # Upload the audio file to the server
            url = f"http://localhost:8000/upload_audio/{st.session_state.project_name}"
            files = {"file": (audio_file.name, audio_file.read(), "audio/wav")}
            response = requests.post(
                url,
                files=files,
            )
            if response.status_code == 200:
                result = response.json()
                if not result["success"]:
                    status_message.error(f"Error : {result['error']}")
                    return
                else:
                    audio_uploaded = True
                    status_message.success("Audio file uploaded successfully!")
            else:
                status_message.error(f"Error for audio upload : {response.status_code}")

            if audio_uploaded:
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
                    if response.json()["success"] is True:
                        status_message.success("Metadata created successfully!")
                    else:
                        status_message.error(f"Failed to create metadata with {error}")
                        return
                else:
                    status_message.error(
                        f"Failed to create metadata with status code {response.status_code}"
                    )
                    return
                status_message.text("Dividing audio into chunks...")
                # Divide the audio file into chunks
                url = (
                    f"http://localhost:8000/get_chunks/{st.session_state.project_name}"
                )
                data = {"bpm": bpm}
                response = requests.post(
                    url,
                    data=data,
                )

                if response.status_code == 200:
                    result = response.json()
                    if not result["success"]:
                        status_message.error(
                            f"Error in audio chunking : {result['error']}"
                        )
                        return
                    else:
                        chunks_created = True
                        status_message.success(
                            "Audio file divided into chunks successfully!"
                        )
                else:
                    status_message.error(
                        f"Error in audio chunking : {response.status_code}"
                    )
                    return
                update_metadata(st.session_state.project_name)

            if audio_uploaded and chunks_created:
                status_message.text("Transcribing audio chunks...")
                # Transcribe the audio chunks
                url = "http://localhost:8000/transcribe_audio_chunks/"
                data = {
                    "project_name": st.session_state.project_name,
                }
                params = {
                    "translation_language": "en",
                }
                response = requests.post(
                    url,
                    data=data,
                    params=params,
                )

                if response.status_code == 200:
                    result = response.json()
                    if not result["success"]:
                        status_message.error(
                            f"Error in transcription : {result['error']}"
                        )
                        return
                    else:
                        # Notify the user that the audio transcription is complete
                        status_message.success("Audio transcription complete")
                else:
                    status_message.error(
                        f"Error in transcription : {response.status_code}"
                    )
                    return
                update_metadata(st.session_state.project_name)
