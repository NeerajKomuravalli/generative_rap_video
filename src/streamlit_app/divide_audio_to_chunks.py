import requests
from typing import Tuple

import streamlit as st

from streamlit_app.update_meta_data import update_metadata
from streamlit_app.project_status import get_project_status


def divide_audio_to_chunks(bpm) -> Tuple[bool, str]:
    # Divide the audio file into chunks
    url = f"http://localhost:8000/get_chunks/{st.session_state.project_name}"
    data = {"bpm": bpm}
    response = requests.post(
        url,
        data=data,
    )

    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            return False, f"Error in audio chunking : {result['error']}"
    else:
        return False, f"Error in audio chunking : {response.status_code}"

    success, message = update_metadata(st.session_state.project_name)
    if not success:
        return False, message

    success, data = get_project_status(st.session_state.project_name)
    if success:
        st.session_state.project_status = data

        return success, None

    return success, data
