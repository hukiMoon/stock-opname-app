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

def tampilkan_sidebar():
    st.sidebar.title("Menu Utama")
    # Tampilkan menu berdasarkan role
    if st.session_state.get("role") == "admin":
        st.sidebar.page_link("pages/4_⚙️_Master_Barang.py", label="Manajemen Master")
    
    st.sidebar.divider()
    
    # Tombol logout selalu muncul jika user login
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.rerun()
