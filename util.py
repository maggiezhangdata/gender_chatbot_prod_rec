from typing import *
import json
import time
from PIL import Image
import streamlit as st
from openai import OpenAI  # Updated import
import requests

def init_session_state():
    if "session_end" not in st.session_state:
        st.session_state.session_end = False

    if "thread_id" not in st.session_state:
        # Create a client instance properly
        client = OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"],
            default_headers={"OpenAI-Beta": "assistants=v2"}
        )
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    if "show_thread_id" not in st.session_state:
        st.session_state.show_thread_id = False

    if 'first_message_sent' not in st.session_state:
        st.session_state.first_message_sent = False

    if 'message_lock' not in st.session_state:
        st.session_state.message_lock = False
    
    if 'duration' not in st.session_state:
        st.session_state.duration = 0
        
    if 'first_input_time' not in st.session_state:
        st.session_state.first_input_time = None
        
    print(f'session duration: {st.session_state.duration}')
    
    if st.session_state.first_input_time:
        print(f'time till now {(time.time() - st.session_state.first_input_time) / 60}')


def refresh_timer():
    if st.session_state.first_input_time:
        st.session_state.duration = (time.time() - st.session_state.first_input_time) / 60
     

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



def update_typing_animation(placeholder, current_dots,partner_names):
    num_dots = (current_dots % 6) + 1  # Cycle through 1 to 3 dots
    placeholder.markdown(f"Waiting for {partner_names} response" + "." * num_dots)
    return num_dots
