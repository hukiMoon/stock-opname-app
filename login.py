# login.py
import streamlit as st

def show_login():
    st.set_page_config(page_title="Login", page_icon="🔐")
    st.title("🔐 Login ke Aplikasi")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Masuk"):
        # Logika validasi (bisa disesuaikan)
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "admin"
            st.rerun()
        else:
            st.error("Username atau password salah!")
