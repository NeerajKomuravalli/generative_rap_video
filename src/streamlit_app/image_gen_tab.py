import requests
from pathlib import Path

import streamlit as st

from segmind.settings import STABLE_DIFFUSION_STYLES
from streamlit_app.models import Type
from streamlit_app.chunk_view_logic import handle_chunk_view


def handle_image_gen_tab():
    # Add a dropdown for the list of styles
    st.session_state.stable_diffussion_style = st.selectbox(
        "Select Style", STABLE_DIFFUSION_STYLES, index=0
    )

    # Add a button to start the stable diffusion
    if st.button("Start Stable Diffusion"):
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
        if response.status_code == 200:
            st.session_state.image_generation_completion = True
            st.success("Stable diffusion started successfully!")
        else:
            st.error("Failed to start stable diffusion.")

    if st.session_state.image_generation_completion or st.button("View Images"):
        url = f"http://localhost:8000/get_images/{st.session_state.project_name}"
        response = requests.get(url)
        # If the request was successful
        if response.status_code == 200 and response.json()["success"] is True:
            # Get the audio chunks from the response
            chunk_images = response.json()["images"]
            # sort audio chunks based on file name "chunk_{index}.wav"
            chunk_images_dict = {
                Path(chunk).stem: chunk
                for chunk in sorted(
                    chunk_images, key=lambda chunk: int(Path(chunk).stem.split("_")[1])
                )
            }
            st.session_state.chunk_images_dict = chunk_images_dict
            st.session_state.get_chunk_image_status = True
            st.session_state.current_chunk_dict["image"]["chunk"] = list(
                chunk_images_dict.keys()
            )[0]
        else:
            # If the request was not successful, display an error message
            st.error(f"Error: {response.status_code}")

    if st.session_state.get_chunk_image_status:
        handle_chunk_view(Type.IMAGE, st.session_state.chunk_images_dict)
