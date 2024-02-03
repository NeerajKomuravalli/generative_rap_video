import streamlit as st

from streamlit_app.initialise_state import init_state
from streamlit_app.start_or_load_project import start_or_load_project
from streamlit_app.transcribe_tab import handle_transcribe_tab
from streamlit_app.prompt_gene_tab import handle_prompt_gene_tab
from streamlit_app.image_gen_tab import handle_image_gen_tab

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
