import streamlit as st
# Pastikan 'bcrypt' ada di file requirements.txt Anda!
import bcrypt 
from db_utils import jalankan_query

def check_role(allowed_roles):
    # Logika tetap sama, tapi pastikan ini dipanggil setelah user login
    if "role" not in st.session_state:
        st.error("Anda belum login!")
        st.stop()
        
    if st.session_state.get("role") not in allowed_roles:
        st.error("🚫 Anda tidak memiliki akses ke halaman ini.")
        st.stop()

    if username_valid and password_valid:
        st.session_state["logged_in"] = True
        st.session_state["role"] = role_dari_db
        st.rerun() # Arahkan ke Beranda setelah login berhasil

def tampilkan_sidebar():
    st.sidebar.title("Menu Utama")
    
    # Navigasi
    if st.session_state.get("role") == "admin":
        st.sidebar.page_link("pages/4_⚙️_Master_Barang.py", label="Manajemen Master")
    
    st.sidebar.divider()
    
    # Tombol logout
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.rerun() # Ini penting agar aplikasi langsung kembali ke layar login
