import streamlit as st

from streamlit_app.initialise_state import init_state
from streamlit_app.start_or_load_project import start_or_load_project
from streamlit_app.transcribe_tab import handle_transcribe_tab
from streamlit_app.prompt_gene_tab import handle_prompt_gene_tab
from streamlit_app.image_gen_tab import handle_image_gen_tab
from streamlit_app.generate_prompt import generate_prompt
from streamlit_app.generate_image import generate_image
from streamlit_app.generate_video import generate_video
from streamlit_app.display_video import display as display_video
from streamlit_app.models import Type

init_state()

st.title("Generate Video")


start_or_load_project()

(
    trascribe_tab,
    prompt_tab,
    images_tab,
) = st.tabs(
    [
        "Transcribe",
        "Prompt",
        "Images",
    ]
)

with trascribe_tab:
    handle_transcribe_tab()

with prompt_tab:
    handle_prompt_gene_tab()

with images_tab:
    handle_image_gen_tab()

if (
    (st.session_state.project_status.transcriptions > 0)
    and (st.session_state.project_status.prompt > 0)
    and (st.session_state.project_status.images > 0)
):
    submit_button = st.button(label="Generate Video", key="generate_video_for_edist")
    if submit_button:
        status_message = st.empty()
        # Figure out what has changed and run only the parts that changed
        if len(st.session_state.updates[Type.TRANSCRIPT.value]):
            if len(st.session_state.updates[Type.PROMPT.value]):
                st.warning(
                    "Found updates in both transcriptions and prompts, prompts will be over written by newly generated transcripts"
                )
            success, message = generate_prompt()
            if not success:
                status_message.error(message)
            else:
                prompts_created = True
                status_message.success("Prompt generated successfully!")

            if prompts_created:
                success, message = generate_image()
                if not success:
                    status_message.error(message)
                else:
                    images_created = True
                    status_message.success("Image generated successfully!")

            if prompts_created and images_created:
                success, message = generate_video()
                if not success:
                    status_message.error(message)
                else:
                    video_created = True
                    status_message.success("Video generated successfully!")

            if video_created:
                display_video()
        elif len(st.session_state.updates[Type.PROMPT.value]):
            success, message = generate_image(
                st.session_state.updates[Type.PROMPT.value]
            )
            if not success:
                status_message.error(message)
            else:
                images_created = True
                status_message.success("Image generated successfully!")

            if images_created:
                success, message = generate_video()
                if not success:
                    status_message.error(message)
                else:
                    video_created = True
                    status_message.success("Video generated successfully!")

            if video_created:
                display_video()
