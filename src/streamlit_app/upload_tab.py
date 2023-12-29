import requests
import streamlit as st

from streamlit_app.update_meta_data import update_metadata


def handle_upload_tab():
    ## audio file
    audio_file = st.file_uploader("Upload your audio file", type=["mp3", "wav"])
    ## bpm
    bpm = st.number_input("Enter the BPM of the track")

    # Submit button
    if st.button("Upload"):
        # Create a for status message
        status_message = st.empty()

        if st.session_state.project_name_state is False:
            st.error("Please enter the project name")
        audio_uploaded = False
        chunks_created = False
        transcription_created = False
        if audio_file and bpm:
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
                    status_message.text("Error")
                    st.error(f"Error : {result['error']}")
                else:
                    audio_uploaded = True
                    st.success("Audio file uploaded successfully!")
            else:
                status_message.text("Error")
                st.error(f"Error for audio upload : {response.status_code}")

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
                        st.success("Metadata created successfully!")
                    else:
                        error = response.json()["error"]
                        st.error(f"Failed to create metadata with {error}")
                else:
                    st.error(
                        f"Failed to create metadata with status code {response.status_code}"
                    )

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
                        status_message.text("Error")
                        st.error(f"Error in audio chunking : {result['error']}")
                    else:
                        chunks_created = True
                        st.success("Audio file divided into chunks successfully!")
                else:
                    status_message.text("Error")
                    st.error(f"Error in audio chunking : {response.status_code}")

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
                        status_message.text("Error")
                        st.error(f"Error in transcription : {result['error']}")
                    else:
                        # Notify the user that the audio transcription is complete
                        transcription_created = True
                        status_message.text("Audio transcription complete")
                        st.success("Audio transcription complete")
                else:
                    status_message.text("Error : ")
                    st.error(f"Error in transcription : {response.status_code}")

                update_metadata(st.session_state.project_name)
