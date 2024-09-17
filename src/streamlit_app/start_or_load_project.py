import streamlit as st

from streamlit_app.project_status import get_project_status
from streamlit_app.generate_prompt import generate_prompt
from streamlit_app.generate_image import generate_image
from streamlit_app.generate_video import generate_video
from streamlit_app.get_meta_data import get_metadata
from streamlit_app.create_project import create_project
from streamlit_app.upload_audio import upload_audio
from streamlit_app.create_metadata import create_metadata
from streamlit_app.divide_audio_to_chunks import divide_audio_to_chunks
from streamlit_app.transcribe_audio_chunks import transcribe_audio_chunks
from streamlit_app.display_video import display as display_video
from streamlit_app.initialise_state import init_state


def start_or_load_project():
    with st.form(key="my_form"):
        project_name = st.text_input("Enter the project name")
        ## audio file
        audio_file = st.file_uploader("Upload your audio file", type=["mp3", "wav"])
        ## bpm
        bpm = st.number_input("Enter the BPM of the track")

        submit_button = st.form_submit_button(label="Generate Video")

        status_message = st.empty()
        if submit_button:
            init_state(reload=True)
            if project_name == "":
                status_message.error("Please enter the project name")

            st.session_state.project_name_state = True
            st.session_state.project_name = project_name

            success, data = create_project()
            if not success:
                status_message.error(data)

            if st.session_state.project_status.original != "":
                if audio_file:
                    # This means user has added an audio file but the project already has an audio file
                    # NOTE: As of now we will notify user about this
                    status_message.error("Project already has audio file")
                    return
                if bpm:
                    # No audio file present but bpm given

                    status_message.error(
                        "You have added a BPM for a project with an audio file and bpm"
                    )
                    return
                # If the project already has an audio file and bpm, we don't need to do anything
                success, data = get_project_status(st.session_state.project_name)
                if success:
                    st.session_state.project_status = data
                else:
                    st.error(data)
                    return

                if st.session_state.project_status.video != "":
                    status_message.success("Project loaded successfully")
                    display_video()
                    return
                else:
                    # NOTE: This is a temporary fix. Based on how much the project is complete, we will start the process
                    status_message.error(
                        "Looks like the project is not complete. Please create a new project and start the process"
                    )
                    return
            else:
                if not (audio_file and bpm):
                    # This means user has not added an audio file or bpm. This is valid when user wants to just create a project
                    status_message.warning(
                        "Project created successfully but no audio file is added"
                    )
                    return

            audio_uploaded = False
            chunks_created = False
            transcripts_created = False
            prompts_created = False
            images_created = False
            video_created = False

            status_message.text("Uploading audio...")
            success, data = upload_audio(audio_file)
            if not success:
                status_message.error(data)
            else:
                audio_uploaded = True
                status_message.success("Audio uploaded successfully!")

            if audio_uploaded:
                success, message = create_metadata(audio_file, bpm)
                if not success:
                    status_message.error(message)
                    return
                else:
                    status_message.success("Metadata created successfully!")

                status_message.text("Dividing audio into chunks...")
                success, message = divide_audio_to_chunks(bpm)
                if not success:
                    status_message.error(message)
                    return
                else:
                    chunks_created = True
                    status_message.success(
                        "Audio file divided into chunks successfully!"
                    )

            success, data = get_metadata(st.session_state.project_name)
            if success:
                st.session_state.metadata = data
            else:
                st.error(data)
                return

            # This will ensure the next step will happen only if audio is uploaded and chunks created
            if (
                audio_uploaded
                and chunks_created
                and (
                    st.session_state.metadata.chunk_count
                    == st.session_state.project_status.audio_chunks
                )
            ):
                status_message.text("Transcribing audio chunks...")
                success, message = transcribe_audio_chunks()
                if not success:
                    status_message.error(message)
                    return
                else:
                    transcripts_created = True
                    status_message.success("Audio transcription complete")

            if (transcripts_created is True) and (
                st.session_state.metadata.chunk_count
                == st.session_state.project_status.transcriptions
            ):
                success, message = generate_prompt()
                if not success:
                    status_message.error(message)
                    return
                else:
                    prompts_created = True
                    status_message.success("Prompt generated successfully!")

            if (prompts_created is True) and (
                st.session_state.metadata.chunk_count
                == st.session_state.project_status.prompt
            ):
                success, message = generate_image()
                if not success:
                    status_message.error(message)
                    return
                else:
                    images_created = True
                    status_message.success("Image generated successfully!")

            if (images_created is True) and (
                st.session_state.metadata.chunk_count
                == st.session_state.project_status.images
            ):
                success, message = generate_video()
                if not success:
                    status_message.error(message)
                    return
                else:
                    video_created = True
                    status_message.success("Video generated successfully!")

            if video_created:
                display_video()
        else:
            if st.session_state.project_status.video != "":
                display_video()
