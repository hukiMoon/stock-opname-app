# styles.py
import streamlit as st

def card_container(title):
    container = st.container(border=True)
    container.markdown(f"### {title}")
    return container
