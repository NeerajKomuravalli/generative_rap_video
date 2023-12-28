from pathlib import Path
from io import BytesIO
import base64
import json

import streamlit as st
import requests

from segmind.settings import STABLE_DIFFUSION_STYLES


# Create state
# Add state for project name
if "project_name" not in st.session_state:
    st.session_state.project_name_state = False
    st.session_state.project_name = ""
if "project_status" not in st.session_state:
    st.session_state.project_status = None

# Add states for the app if not added already
if "upload_button_state" not in st.session_state:
    st.session_state.upload_button_state = False
if "get_audio_chunks_button_state" not in st.session_state:
    st.session_state.get_audio_chunks_button_state = False
    st.session_state.get_audio_chunks_button_data = None
# Initialize the current chunk in the session state for displaying the chunk related information
if "current_chunk" not in st.session_state:
    st.session_state.current_chunk = None
    st.session_state.previous_chunk = None
    st.session_state.chunk_count = 0
    st.session_state.transcript = None
    st.session_state.audio = None
if "stable_diffussion_style" not in st.session_state:
    st.session_state.stable_diffussion_style = STABLE_DIFFUSION_STYLES[0]
if "prompt_generation_completion" not in st.session_state:
    st.session_state.prompt_generation_completion = False
if "chunk_prompts_dict" not in st.session_state:
    st.session_state.chunk_prompts_dict = None
    st.session_state.get_chunk_prompt_status = False
    st.session_state.current_prompt_chunk = None
    st.session_state.previous_prompt_chunk = None
    st.session_state.chunk_prompt_count = 0
    st.session_state.prompt = None


def get_index_from_chunk(chunk: str):
    return int(chunk.split("_")[1])


# Title of the app
st.title("Audio Transcription and Video Generation App")

# Audio files uploader
with st.form(key="my_form"):
    project_name = st.text_input("Enter the project name")
    submit_button = st.form_submit_button(label="Submit")
    if submit_button:
        st.session_state.project_name_state = True
        st.session_state.project_name = project_name

        # Define the URL of the endpoint
        url = f"http://localhost:8000/create_project/{project_name}"

        # Send a POST request to the endpoint
        response = requests.post(url)

        # Check the response
        if response.status_code == 200:
            if response.json()["success"] is True:
                st.success("Project created successfully!")
            else:
                error = response.json()["error"]
                st.error(f"Failed to create project with {error}")
        else:
            st.error(
                f"Failed to create project with status code {response.status_code}"
            )

        url = f"http://localhost:8000/project_status/{project_name}"

        # Send a POST request to the endpoint
        response = requests.get(url)
        if response.status_code == 200:
            if response.json()["success"] is True:
                st.session_state.project_status = response.json()["status"]
            else:
                error = response.json()["error"]
                st.error(f"Failed to get project status with {error}")
        else:
            st.error(f"Failed to get project status with code {response.status_code}")

## audio file
audio_file = st.file_uploader("Upload your audio file", type=["mp3", "wav"])
## bpm
bpm = st.number_input("Enter the BPM of the track")
# Create a for status message
status_message = st.empty()

# Submit button
if st.button("Upload"):
    if st.session_state.project_name_state is False:
        st.error("Please enter the project name")
    audio_uploaded = False
    chunks_created = False
    transcription_created = False
    if audio_file and bpm:
        status_message.text("Processing...")
        # Upload the audio file to the server
        url = f"http://localhost:8000/upload_audio/{st.session_state.project_name}"
        files = {"file": (audio_file.name, audio_file.read(), "audio/wav")}
        response = requests.post(
            url,
            files=files,
        )
        if response.status_code == 200:
            result = response.json()
            if not result["success"]:
                st.error(f"Error : {result['error']}")
            else:
                audio_uploaded = True
                st.success("Audio file uploaded successfully!")
        else:
            st.error(f"Error for audio upload : {response.status_code}")

        if audio_uploaded:
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
                    st.error(f"Error in audio chunking : {result['error']}")
                else:
                    chunks_created = True
                    st.success("Audio file divided into chunks successfully!")
            else:
                st.error(f"Error in audio chunking : {response.status_code}")

        if audio_uploaded and chunks_created:
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
                    st.error(f"Error in transcription : {result['error']}")
                else:
                    # Notify the user that the audio transcription is complete
                    transcription_created = True
                    status_message.text("Audio transcription complete")
                    st.success("Audio transcription complete")
            else:
                status_message.text("Error : ", response.status_code)
                st.error(f"Error in transcription : {response.status_code}")


# When the user clicks the 'Get Audio Chunks' button
if st.button("View transcript and audio"):
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
        st.session_state.current_chunk = list(audio_chunks_dict.keys())[0]
        # Set the chunk count
        st.session_state.chunk_count = len(audio_chunks_dict)
    else:
        # If the request was not successful, display an error message
        st.error(f"Error: {response.status_code}")

if (
    st.session_state.project_name_state is True
    and st.session_state.get_audio_chunks_button_state is True
):
    # Get the audio chunks data from the session state
    audio_chunks_dict = st.session_state.get_audio_chunks_button_data
    audio_chunks_dict_keys = list(audio_chunks_dict.keys())

    # Create a container for the chunk buttons
    expander = st.expander("Select Chunk:")

    with expander:
        # Display the audio chunks
        for i in range(0, len(audio_chunks_dict), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(audio_chunks_dict):
                    chunk = audio_chunks_dict_keys[i + j]
                    if cols[j].button(chunk):
                        # NOTE: FIX IT: When the button is pressed twice consequetively, the current chunk and previous chunk are the same and when the app reloads we will not see the transcript and audio
                        st.session_state.current_chunk = chunk

    # Create next and previous button to naviagte between chunks
    # Get the list of chunks
    chunks = list(audio_chunks_dict.keys())

    # Add next and previous buttons
    next_prev_cols = st.columns(2)
    prev_button = next_prev_cols[0].button("Previous")
    next_button = next_prev_cols[1].button("Next")

    # Update the current chunk based on the button pressed
    if prev_button:
        # Find the index of the current chunk
        index = chunks.index(st.session_state.current_chunk)
        # If it's not the first chunk, move to the previous chunk
        if index > 0:
            st.session_state.current_chunk = chunks[index - 1]
        else:
            # Do round robin
            st.session_state.current_chunk = chunks[-1]
    elif next_button:
        # Find the index of the current chunk
        index = chunks.index(st.session_state.current_chunk)
        # If it's not the last chunk, move to the next chunk
        if index < len(chunks) - 1:
            st.session_state.current_chunk = chunks[index + 1]
        else:
            # Do round robin
            st.session_state.current_chunk = chunks[0]

    # Display the current chunk
    if st.session_state.previous_chunk != st.session_state.current_chunk:
        # Make a GET request to the 'get_transcript' endpoint
        response_transcript = requests.get(
            f"http://localhost:8000/get_transcript/{st.session_state.project_name}/{st.session_state.current_chunk}"
        )

        # If the request was successful
        transcript_data = response_transcript.json()
        if (response_transcript.status_code == 200) and (
            transcript_data["success"] is True
        ):
            st.session_state.transcript = transcript_data["transcription"]

            # Make a GET request to the 'get_audio_chunk' endpoint
            response_audio_chunk = requests.get(
                f"http://localhost:8000/get_audio_chunk/{st.session_state.project_name}/{st.session_state.current_chunk}"
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
                st.session_state.audio = BytesIO(audio_bytes)
            else:
                st.error(
                    f"Error in getting audio chunk: {response_audio_chunk.status_code}"
                )
        else:
            st.error(f"Error in getting transcript: {response_transcript.status_code}")

        # Set the previous chunk to the current chunk
        st.session_state.previous_chunk = st.session_state.current_chunk

    # Display the transcript
    transcript_edited = st.text_area(
        "Transcript",
        json.dumps(st.session_state.transcript, indent=4),
        height=250,
    )

    # Add a button to submit the edited transcript
    if st.button("Update Transcript"):
        # Define the URL of the endpoint
        url = f"http://localhost:8000/update_transcription/{st.session_state.project_name}/{st.session_state.current_chunk}"

        # Define the data to be sent to the endpoint
        data = json.loads(transcript_edited)

        # Send a POST request to the endpoint
        response = requests.put(url, json=data)
        st.write(response.json())
        # Check the response
        if response.status_code == 200 and response.json()["success"] is True:
            st.session_state.transcript = json.loads(transcript_edited)
            st.success("Transcript updated successfully!")
        else:
            # display message on ui
            st.write(response.json())
            st.error("Failed to update transcript.")

    # Display the audio
    st.audio(st.session_state.audio, format="audio/wav")

    # Display the current chunk name
    st.write(st.session_state.current_chunk)

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

if st.session_state.prompt_generation_completion or st.button("View Generated Prompts"):
    url = f"http://localhost:8000/get_sd_prompts/{st.session_state.project_name}"
    response = requests.get(url)
    # If the request was successful
    if response.status_code == 200:
        # Get the audio chunks from the response
        chunk_prompts = response.json()["prompts"]
        # sort audio chunks based on file name "chunk_{index}.wav"
        chunk_prompts_dict = {
            "Prompt" + Path(chunk).stem: chunk
            for chunk in sorted(
                chunk_prompts, key=lambda chunk: int(Path(chunk).stem.split("_")[1])
            )
        }
        st.session_state.chunk_prompts_dict = chunk_prompts_dict
        st.session_state.get_chunk_prompt_status = True
        st.session_state.current_prompt_chunk = list(chunk_prompts_dict.keys())[0]
        st.session_state.chunk_prompt_count = len(chunk_prompts_dict)
    else:
        # If the request was not successful, display an error message
        st.error(f"Error: {response.status_code}")

if st.session_state.get_chunk_prompt_status:
    chunk_prompts_dict = st.session_state.chunk_prompts_dict
    chunk_prompts_dict_keys = list(chunk_prompts_dict.keys())

    # Create a container for the chunk buttons
    expander = st.expander("Select Chunk:")

    with expander:
        # Display the audio chunks
        for i in range(0, len(chunk_prompts_dict), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(chunk_prompts_dict):
                    chunk = chunk_prompts_dict_keys[i + j]
                    if cols[j].button(chunk):
                        # NOTE: FIX IT: When the button is pressed twice consequetively, the current chunk and previous chunk are the same and when the app reloads we will not see the transcript and audio
                        st.session_state.current_prompt_chunk = chunk

    # Create next and previous button to naviagte between chunks
    # Get the list of chunks
    chunks = list(chunk_prompts_dict.keys())

    # Add next and previous buttons
    next_prev_cols = st.columns(2)
    prev_button = next_prev_cols[0].button("Previous prompt")
    next_button = next_prev_cols[1].button("Next prompt")

    # Update the current chunk based on the button pressed
    if prev_button:
        # Find the index of the current chunk
        index = chunks.index(st.session_state.current_prompt_chunk)
        # If it's not the first chunk, move to the previous chunk
        if index > 0:
            st.session_state.current_prompt_chunk = chunks[index - 1]
        else:
            # Do round robin
            st.session_state.current_prompt_chunk = chunks[-1]
    elif next_button:
        # Find the index of the current chunk
        index = chunks.index(st.session_state.current_prompt_chunk)
        # If it's not the last chunk, move to the next chunk
        if index < len(chunks) - 1:
            st.session_state.current_prompt_chunk = chunks[index + 1]
        else:
            # Do round robin
            st.session_state.current_prompt_chunk = chunks[0]

    if st.session_state.previous_prompt_chunk != st.session_state.current_prompt_chunk:
        # Make a GET request to the 'get_transcript' endpoint
        response_prompt = requests.get(
            f"http://localhost:8000/get_sd_prompt/{st.session_state.project_name}/{st.session_state.current_prompt_chunk}"
        )

        # If the request was successful
        prompt_data = response_prompt.json()
        if (response_prompt.status_code == 200) and (prompt_data["success"] is True):
            st.session_state.prompt = prompt_data["prompt"]

            # Make a GET request to the 'get_audio_chunk' endpoint
            response_audio_chunk = requests.get(
                f"http://localhost:8000/get_audio_chunk/{st.session_state.project_name}/{st.session_state.current_prompt_chunk}"
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
                st.session_state.audio = BytesIO(audio_bytes)
            else:
                st.error(
                    f"Error in getting audio chunk: {response_audio_chunk.status_code}"
                )
        else:
            st.error(f"Error in getting prompt: {response_prompt.status_code}")

        # Set the previous chunk to the current chunk
        st.session_state.previous_prompt_chunk = st.session_state.current_prompt_chunk

    # Display the prompt
    prompt_edited = st.text_area(
        "Prompt",
        st.session_state.prompt,
        height=250,
    )

    # Add a button to submit the edited prompt
    if st.button("Update Prompt"):
        # Define the URL of the endpoint
        url = f"http://localhost:8000/update_sd_prompt/{st.session_state.project_name}/{st.session_state.current_prompt_chunk}"

        # Define the data to be sent to the endpoint
        data = {
            "updated_sd_prompt": prompt_edited,
        }

        # Send a POST request to the endpoint
        response = requests.put(url, json=data)

        # Check the response
        if response.status_code == 200 and response.json()["success"] is True:
            st.session_state.prompt = prompt_edited
            st.success("Prompt updated successfully!")
        else:
            # display message on ui
            st.write(response.json())
            st.error("Failed to update prompt.")

    # Display the audio
    st.audio(st.session_state.audio, format="audio/wav")

    # Display the current chunk name
    st.write(st.session_state.current_prompt_chunk)


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
        st.success("Stable diffusion started successfully!")
    else:
        st.error("Failed to start stable diffusion.")

if st.button("Generate Video"):
    url = "http://localhost:8000/generate_video"
    data = {
        "project_name": st.session_state.project_name,
    }

    response = requests.post(url, data=data)

    if response.status_code == 200 and response.json()["success"] is True:
        st.success("Video generated successfully!")
    else:
        st.write(response.json()["error"])
        st.error("Failed to generate video.")
