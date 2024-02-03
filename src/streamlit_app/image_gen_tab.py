import requests
from pathlib import Path

import streamlit as st

from segmind.settings import STABLE_DIFFUSION_STYLES
from streamlit_app.models import Type
from streamlit_app.chunk_view_logic import handle_chunk_view
from streamlit_app.get_audio_data import get_audio_chunk
from streamlit_app.generate_image import generate_image


def handle_image_gen_tab():
    if (
        st.session_state.image_generation_completion
        or st.session_state.project_status.images > 0
    ) and (st.session_state.image_tab_load):
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
            st.session_state.current_chunk_dict[Type.IMAGE.value]["chunk"] = list(
                chunk_images_dict.keys()
            )[0]

            status_code, audio_data = get_audio_chunk(
                st.session_state.project_name,
                st.session_state.current_chunk_dict[Type.IMAGE.value]["chunk"],
            )
            if audio_data is None:
                st.error(f"Error in getting audio chunk: {status_code}")
            st.session_state.current_chunk_dict[Type.IMAGE.value]["audio"] = audio_data
            st.session_state.image_tab_load = False
        else:
            # If the request was not successful, display an error message
            st.error(f"Error: {response.status_code}")

    if st.session_state.get_chunk_image_status:
        handle_chunk_view(Type.IMAGE, st.session_state.chunk_images_dict)


def handle_image_gen_tab_v1():
    # Add a dropdown for the list of styles
    st.session_state.stable_diffussion_style = st.selectbox(
        "Select Style", STABLE_DIFFUSION_STYLES, index=0
    )

    # Add a button to start the stable diffusion
    if st.button("Start Stable Diffusion"):
        success, message = generate_image()
        if not success:
            st.error(message)

    handle_image_gen_tab()
