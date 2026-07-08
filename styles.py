import streamlit as st

def apply_modern_style():
    # Menghilangkan elemen default Streamlit yang mengganggu
    hide_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 2rem;}
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

def card_container(title):
    # Membuat pembungkus dengan border agar terlihat seperti kartu
    return st.container(border=True)
