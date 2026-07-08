# styles.py
import streamlit as st

def card_container(title):
    """
    Membuat container dengan border dan judul agar tampilan 
    setiap menu terlihat seragam dan profesional.
    """
    container = st.container(border=True)
    container.markdown(f"### {title}")
    return container
