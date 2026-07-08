# auth.py
import streamlit as st

def check_password():
    """Fungsi untuk mengecek apakah user sudah login."""
    if "login_sukses" not in st.session_state:
        st.session_state.login_sukses = False

    if not st.session_state.login_sukses:
        st.title("🔐 Login Admin")
        password = st.text_input("Masukkan Password", type="password")
        if st.button("Login"):
            if password == "admin123":  # Ganti dengan password yang diinginkan
                st.session_state.login_sukses = True
                st.rerun()
            else:
                st.error("Password salah!")
        st.stop() # Menghentikan sisa kode agar tidak tampil sebelum login

def sidebar_logout():
    if st.session_state.login_sukses:
        st.sidebar.divider()
        if st.sidebar.button("Logout"):
            st.session_state.login_sukses = False
            st.rerun()
