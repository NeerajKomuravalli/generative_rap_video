import requests
from typing import Tuple

import streamlit as st

from streamlit_app.update_meta_data import update_metadata
from streamlit_app.project_status import get_project_status


def transcribe_audio_chunks() -> Tuple[bool, str]:
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
            return False, f"Error in transcription : {result['error']}"
    else:
        return False, f"Error in transcription : {response.status_code}"

    success, message = update_metadata(st.session_state.project_name)
    if not success:
        return False, message

    success, data = get_project_status(st.session_state.project_name)
    if success:
        st.session_state.project_status = data

        return success, None

    return success, data
