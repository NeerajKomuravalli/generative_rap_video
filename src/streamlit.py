import streamlit as st

from streamlit_app.initialise_state import init_state
from streamlit_app.project_tab import handle_project_tab
from streamlit_app.upload_tab import handle_upload_tab
from streamlit_app.transcribe_tab import handle_transcribe_tab
from streamlit_app.prompt_gene_tab import handle_prompt_gene_tab
from streamlit_app.image_gen_tab import handle_image_gen_tab
from streamlit_app.video_gen_tab import handle_video_gen_tab


init_state()

# Title of the app
st.title("Audio Transcription and Video Generation App")

# Create a tab bar with two tabs
(
    project_tab,
    upload_tab,
    transcribe_tab,
    prompt_gene_tab,
    image_gen_tab,
    video_gen_tab,
) = st.tabs(
    [
        "Start Project",
        "Upload",
        "Transcribe",
        "Prompt",
        "Generate Images",
        "Generate Video",
    ]
)

with project_tab:
    handle_project_tab()

with upload_tab:
    handle_upload_tab()

with transcribe_tab:
    handle_transcribe_tab()

with prompt_gene_tab:
    handle_prompt_gene_tab()

with image_gen_tab:
    handle_image_gen_tab()

with video_gen_tab:
    handle_video_gen_tab()
