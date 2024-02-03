import streamlit as st

from segmind.settings import STABLE_DIFFUSION_STYLES
from streamlit_app.project_status import get_project_status
from data_exchange.models import ProjectStatus
from data_exchange.models import ProjectData


def init_state(reload: bool = False):
    """
    We use this function to set the initial state for the app.
    We can use reload argument to do a hard reset of the state if needed.
    """
    # Create state
    # Add state for project name
    if ("project_name" not in st.session_state) or reload:
        st.session_state.project_name_state = False
        st.session_state.project_name = ""
    if ("project_status" not in st.session_state) or reload:
        st.session_state.project_status = ProjectStatus()
    if ("metadata" not in st.session_state) or reload:
        st.session_state.metadata = ProjectData()
    # Add states for the app if not added already
    if ("upload_button_state" not in st.session_state) or reload:
        st.session_state.upload_button_state = False
    if ("get_audio_chunks_button_state" not in st.session_state) or reload:
        st.session_state.get_audio_chunks_button_state = False
        st.session_state.get_audio_chunks_button_data = None
    # Initialize the current chunk in the session state for displaying the chunk related information
    if ("current_chunk_dict" not in st.session_state) or reload:
        st.session_state.current_chunk_dict = {
            "transcript": {
                "chunk": None,
                "audio": None,
                "data": None,
            },
            "prompt": {
                "chunk": None,
                "audio": None,
                "data": None,
            },
            "image": {
                "chunk": None,
                "audio": None,
                "data": None,
            },
        }
        st.session_state.previous_chunk_dict = {
            "transcript": {
                "chunk": None,
                "audio": None,
                "data": None,
            },
            "prompt": {
                "chunk": None,
                "audio": None,
                "data": None,
            },
            "image": {
                "chunk": None,
                "audio": None,
                "data": None,
            },
        }
        st.session_state.chunk_count = 0
    if ("stable_diffussion_style" not in st.session_state) or reload:
        st.session_state.stable_diffussion_style = STABLE_DIFFUSION_STYLES[0]
    if ("prompt_generation_completion" not in st.session_state) or reload:
        st.session_state.prompt_generation_completion = False
    if ("image_generation_completion" not in st.session_state) or reload:
        st.session_state.image_generation_completion = False
    if ("chunk_prompts_dict" not in st.session_state) or reload:
        st.session_state.chunk_prompts_dict = None
        st.session_state.get_chunk_prompt_status = False
        st.session_state.current_prompt_chunk = None
        st.session_state.previous_prompt_chunk = None
        st.session_state.chunk_prompt_count = 0
        st.session_state.prompt = None
    if ("get_chunk_image_status" not in st.session_state) or reload:
        st.session_state.get_chunk_image_status = False
    # Tab loading states
    if ("transcribe_tab_load" not in st.session_state) or reload:
        st.session_state.transcribe_tab_load = True
    if ("prompt_tab_load" not in st.session_state) or reload:
        st.session_state.prompt_tab_load = True
    if ("image_tab_load" not in st.session_state) or reload:
        st.session_state.image_tab_load = True
    # Track all the updated transcripts and prompts
    if ("updates" not in st.session_state) or reload:
        st.session_state.updates = {
            "transcript": [],
            "prompt": [],
        }
