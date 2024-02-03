import requests

from pathlib import Path
import streamlit as st

from streamlit_app.models import Type
from streamlit_app.chunk_view_logic import handle_chunk_view
from streamlit_app.get_audio_data import get_audio_chunk


def handle_transcribe_tab():
    # When the user clicks the 'Get Audio Chunks' button
    # if st.button("View transcript and audio"):
    if (
        st.session_state.project_status.transcriptions > 0
        and st.session_state.transcribe_tab_load is True
    ):
        # if st.session_state.project_name_state is True:
        if st.session_state.project_name_state is False:
            st.error("Please enter the project name")

        # Make a GET request to the 'get_audio_chunks' endpoint
        response = requests.get(
            f"http://localhost:8000/get_audio_chunks/",
            params={"project_name": st.session_state.project_name},
        )

        # If the request was successful
        if response.status_code == 200:
            # Get the audio chunks from the response
            audio_chunks = response.json()["audio_chunks"]

            # sort audio chunks based on file name "chunk_{index}.wav"
            audio_chunks_dict = {
                Path(chunk).stem: chunk
                for chunk in sorted(
                    audio_chunks, key=lambda chunk: int(Path(chunk).stem.split("_")[1])
                )
            }

            # set the get_audio_chunks_button_state to True
            st.session_state.get_audio_chunks_button_state = True

            # set the get_audio_chunks_button_data to the audio_chunks_dict
            st.session_state.get_audio_chunks_button_data = audio_chunks_dict
            # Set the current state to the first chunk
            st.session_state.current_chunk_dict[Type.TRANSCRIPT.value]["chunk"] = list(
                audio_chunks_dict.keys()
            )[0]
            status_code, audio_data = get_audio_chunk(
                st.session_state.project_name,
                st.session_state.current_chunk_dict[Type.TRANSCRIPT.value]["chunk"],
            )
            if audio_data is None:
                st.error(f"Error in getting audio chunk: {status_code}")
            st.session_state.current_chunk_dict[Type.TRANSCRIPT.value][
                "audio"
            ] = audio_data

            # Set the chunk count
            st.session_state.chunk_count = len(audio_chunks_dict)
            st.session_state.transcribe_tab_load = False
        else:
            # If the request was not successful, display an error message
            st.error(f"Error: {response.status_code}")

    if (
        st.session_state.project_name_state is True
        and st.session_state.get_audio_chunks_button_state is True
    ):
        handle_chunk_view(
            Type.TRANSCRIPT, st.session_state.get_audio_chunks_button_data
        )
