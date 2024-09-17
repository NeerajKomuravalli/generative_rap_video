import requests
from typing import Tuple

import streamlit as st

from streamlit_app.project_status import get_project_status


def upload_audio(audio_file) -> Tuple[bool, str]:
    url = f"http://localhost:8000/upload_audio/{st.session_state.project_name}"
    files = {"file": (audio_file.name, audio_file.read(), "audio/wav")}
    response = requests.post(
        url,
        files=files,
    )
    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            return False, f"Error : {result['error']}"
    else:
        return False, f"Error for audio upload : {response.status_code}"

    success, data = get_project_status(st.session_state.project_name)
    if success:
        st.session_state.project_status = data

        return success, None

    return success, data
