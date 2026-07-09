import streamlit as st

def form_login():
    st.subheader("Login ke Aplikasi")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Masuk"):
        # Ganti dengan logika validasi database Anda
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "admin"
            st.rerun()
        else:
            st.error("Username atau password salah!")

def tampilkan_sidebar():
    st.sidebar.title("Menu Utama")
    if st.session_state.get("role") == "admin":
        st.sidebar.page_link("pages/4_⚙️_Master_Barang.py", label="Manajemen Master")
    
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.rerun()
