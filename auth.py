import streamlit as st
import bcrypt
from db_utils import jalankan_query

def check_role(allowed_roles):
    """
    Fungsi untuk memeriksa apakah user saat ini memiliki akses.
    allowed_roles: list atau string, misal: ["admin", "editor"]
    """
    # Ambil role dari session_state
    current_role = st.session_state.get("role", None)

    # Jika role tidak ada atau tidak termasuk dalam list yang diizinkan
    if current_role not in allowed_roles:
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
