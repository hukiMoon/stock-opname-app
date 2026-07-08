import streamlit as st
import bcrypt
from db_utils import jalankan_query

def check_password(username, password):
    # Ambil data user dari DB
    query = "SELECT password_hash, role FROM users WHERE username = ?"
    user_data = jalankan_query(query, (username,), fetch=True)
    
    if user_data:
        stored_hash = user_data[0][0]
        user_role = user_data[0][1]
        
        # Verifikasi password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            st.session_state["logged_in"] = True
            st.session_state["role"] = user_role
            st.session_state["username"] = username
            return True
    
    return False

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
