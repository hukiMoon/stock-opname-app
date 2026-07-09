# styles.py
import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def card_container(title):
    """
    Membuat container dengan border dan judul agar tampilan 
    setiap menu terlihat seragam dan profesional.
    """
    container = st.container(border=True)
    container.markdown(f"### {title}")
    return container
