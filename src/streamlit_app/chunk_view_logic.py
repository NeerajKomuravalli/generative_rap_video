import requests
import json
import base64
from io import BytesIO

from PIL import Image
import streamlit as st

from streamlit_app.models import Type


def handle_chunk_view(type: Type, chunk_data: dict):
    # Get the audio chunks data from the session state
    audio_chunks_dict_keys = list(chunk_data.keys())

    # Create a container for the chunk buttons
    expander = st.expander("Select Chunk:")
    with expander:
        # Display the audio chunks
        for i in range(0, len(chunk_data), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(chunk_data):
                    chunk = audio_chunks_dict_keys[i + j]
                    if cols[j].button(chunk, key=f"{type.value}_{chunk}"):
                        # NOTE: FIX IT: When the button is pressed twice consequetively, the current chunk and previous chunk are the same and when the app reloads we will not see the transcript and audio
                        st.session_state.current_chunk_dict[type.value]["chunk"] = chunk

    # Create next and previous button to naviagte between chunks
    # Get the list of chunks
    chunks = list(chunk_data.keys())

    # Add next and previous buttons
    next_prev_cols = st.columns(2)
    prev_button = next_prev_cols[0].button("Previous", key=f"{type.value}_prev")
    next_button = next_prev_cols[1].button("Next", key=f"{type.value}_next")

    # Update the current chunk based on the button pressed
    if prev_button:
        # Find the index of the current chunk
        index = chunks.index(st.session_state.current_chunk_dict[type.value]["chunk"])
        # If it's not the first chunk, move to the previous chunk
        if index > 0:
            st.session_state.current_chunk_dict[type.value]["chunk"] = chunks[index - 1]
        else:
            # Do round robin
            st.session_state.current_chunk_dict[type.value]["chunk"] = chunks[-1]
    elif next_button:
        # Find the index of the current chunk
        index = chunks.index(st.session_state.current_chunk_dict[type.value]["chunk"])
        # If it's not the last chunk, move to the next chunk
        if index < len(chunks) - 1:
            st.session_state.current_chunk_dict[type.value]["chunk"] = chunks[index + 1]
        else:
            # Do round robin
            st.session_state.current_chunk_dict[type.value]["chunk"] = chunks[0]

    # Display the current chunk
    if (
        st.session_state.previous_chunk_dict[type.value]["chunk"]
        != st.session_state.current_chunk_dict[type.value]["chunk"]
    ):
        # Make a GET request to the 'get_transcript' endpoint
        if type == Type.TRANSCRIPT:
            response = requests.get(
                f"http://localhost:8000/get_transcript/{st.session_state.project_name}/{st.session_state.current_chunk_dict[type.value]['chunk']}"
            )
        elif type == Type.PROMPT:
            response = requests.get(
                f"http://localhost:8000/get_sd_prompt/{st.session_state.project_name}/{st.session_state.current_chunk_dict[type.value]['chunk']}"
            )
        elif type == Type.IMAGE:
            response = requests.get(
                f"http://localhost:8000/get_image/{st.session_state.project_name}/{st.session_state.current_chunk_dict[type.value]['chunk']}"
            )
        else:
            st.error("Invalid type")

        # If the request was successful
        response_data = response.json()
        if (response.status_code == 200) and (response_data["success"] is True):
            if type == Type.TRANSCRIPT:
                st.session_state.current_chunk_dict[type.value]["data"] = response_data[
                    "transcription"
                ]
            elif type == Type.PROMPT:
                st.session_state.current_chunk_dict[type.value]["data"] = response_data[
                    "prompt"
                ]
            elif type == Type.IMAGE:
                st.session_state.current_chunk_dict[type.value]["data"] = response_data[
                    "image"
                ]
            else:
                st.error("Invalid type")

            # Make a GET request to the 'get_audio_chunk' endpoint
            response_audio_chunk = requests.get(
                f"http://localhost:8000/get_audio_chunk/{st.session_state.project_name}/{st.session_state.current_chunk_dict[type.value]['chunk']}"
            )

            audio_data = response_audio_chunk.json()
            # If the request was successful
            if (response_audio_chunk.status_code == 200) and (
                audio_data["success"] is True
            ):
                audio_file = audio_data["audio"]

                # Decode the base64 string to bytes
                audio_bytes = base64.b64decode(audio_file)

                # Convert the audio file to a BytesIO object
                st.session_state.current_chunk_dict[type.value]["audio"] = BytesIO(
                    audio_bytes
                )
            else:
                st.error(
                    f"Error in getting audio chunk: {response_audio_chunk.status_code}"
                )
        else:
            st.error(f"Error in getting transcript: {response.status_code}")

        # Set the previous chunk to the current chunk
        st.session_state.previous_chunk_dict[type.value][
            "chunk"
        ] = st.session_state.current_chunk_dict[type.value]["chunk"]

    if type in [Type.TRANSCRIPT, type.PROMPT]:
        # Display the transcript
        transcript_edited = st.text_area(
            "Transcript",
            json.dumps(
                st.session_state.current_chunk_dict[type.value]["data"], indent=4
            ),
            height=250,
        )
    elif type == Type.IMAGE:
        # Convert the image data to a PIL Image objec
        image_data = st.session_state.current_chunk_dict[type.value]["data"]
        image = Image.open(BytesIO(image_data))

        # Display the image
        st.image(image)

        st.image()

    # Add a button to submit the edited transcript
    if type in [Type.TRANSCRIPT, type.PROMPT]:
        if st.button("Update", key=f"{type.value}_update"):
            # Define the URL of the endpoint
            url = f"http://localhost:8000/update_transcription/{st.session_state.project_name}/{st.session_state.current_chunk_dict[type.value]['chunk']}"

            # Define the data to be sent to the endpoint
            data = json.loads(transcript_edited)

            # Send a POST request to the endpoint
            response = requests.put(url, json=data)
            st.write(response.json())
            # Check the response
            if response.status_code == 200 and response.json()["success"] is True:
                st.session_state.current_chunk_dict[type.value]["data"] = json.loads(
                    transcript_edited
                )
                st.success("Transcript updated successfully!")
            else:
                # display message on ui
                st.write(response.json())
                st.error("Failed to update transcript.")

    # Display the audio
    st.audio(
        st.session_state.current_chunk_dict[type.value]["audio"], format="audio/wav"
    )

    # Display the current chunk name
    st.write(st.session_state.current_chunk_dict[type.value]["chunk"])
