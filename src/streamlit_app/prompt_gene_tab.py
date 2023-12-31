import requests
import base64
from io import BytesIO

from pathlib import Path
import streamlit as st

from streamlit_app.models import Type
from streamlit_app.chunk_view_logic import handle_chunk_view
from streamlit_app.get_audio_data import get_audio_chunk


def handle_prompt_gene_tab():
    # Add a button to generate a prompt
    if st.button("Generate Prompt"):
        # Define the URL of the endpoint
        url = "http://localhost:8000/generate_prompts"

        # Define the data to be sent to the endpoint
        data = {
            "project_name": st.session_state.project_name,
        }

        # Send a POST request to the endpoint
        response = requests.post(url, data=data)

        # Check the response
        if response.status_code == 200:
            st.session_state.prompt_generation_completion = True
            st.success("Prompts generated successfully!")
        else:
            st.error("Failed to generate prompts.")

    if (
        st.session_state.prompt_generation_completion
        or st.session_state.project_status.prompt > 0
    ):
        url = f"http://localhost:8000/get_sd_prompts/{st.session_state.project_name}"
        response = requests.get(url)
        # If the request was successful
        if response.status_code == 200:
            # Get the audio chunks from the response
            chunk_prompts = response.json()["prompts"]
            # sort audio chunks based on file name "chunk_{index}.wav"
            chunk_prompts_dict = {
                Path(chunk).stem: chunk
                for chunk in sorted(
                    chunk_prompts, key=lambda chunk: int(Path(chunk).stem.split("_")[1])
                )
            }
            st.session_state.chunk_prompts_dict = chunk_prompts_dict
            st.session_state.get_chunk_prompt_status = True
            st.session_state.current_chunk_dict[Type.PROMPT.value]["chunk"] = list(
                chunk_prompts_dict.keys()
            )[0]

            status_code, audio_data = get_audio_chunk(
                st.session_state.project_name,
                st.session_state.current_chunk_dict[Type.PROMPT.value]["chunk"],
            )
            if audio_data is None:
                st.error(f"Error in getting audio chunk: {status_code}")
            st.session_state.current_chunk_dict[Type.PROMPT.value]["audio"] = audio_data

            st.session_state.chunk_prompt_count = len(chunk_prompts_dict)
        else:
            # If the request was not successful, display an error message
            st.error(f"Error: {response.status_code}")

    if st.session_state.get_chunk_prompt_status:
        handle_chunk_view(Type.PROMPT, st.session_state.chunk_prompts_dict)