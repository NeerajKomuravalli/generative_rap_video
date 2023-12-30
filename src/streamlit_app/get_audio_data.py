import requests
import base64
from io import BytesIO


def get_audio_chunk(project_name: str, chunk_name: str):
    # Make a GET request to the 'get_audio_chunk' endpoint
    response_audio_chunk = requests.get(
        f"http://localhost:8000/get_audio_chunk/{project_name}/{chunk_name}"
    )

    audio_data = response_audio_chunk.json()
    # If the request was successful
    if (response_audio_chunk.status_code == 200) and (audio_data["success"] is True):
        audio_file = audio_data["audio"]

        # Decode the base64 string to bytes
        audio_bytes = base64.b64decode(audio_file)

        # Convert the audio file to a BytesIO object
        return response_audio_chunk.status_code, BytesIO(audio_bytes)
    else:
        return response_audio_chunk.status_code, None
