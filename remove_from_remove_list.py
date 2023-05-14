import streamlit as st

def remove(session_state_attribute,session_state_value):
    st.session_state[session_state_attribute].append(session_state_value)