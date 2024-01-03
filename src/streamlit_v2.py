import streamlit as st

from streamlit_app.initialise_state import init_state
from streamlit_app.start_or_load_project import start_or_load_project
from streamlit_app.run_all import run_all

init_state()

st.title("Generate Video")


start_or_load_project()

run_all()
