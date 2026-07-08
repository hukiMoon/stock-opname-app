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

def sidebar_logout():
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.session_state["username"] = None
        st.rerun()

def logout():
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None
    st.rerun()
