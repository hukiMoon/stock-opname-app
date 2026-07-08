# auth.py
import streamlit as st

def check_password():
    # ... logika pengecekan password ...
    if password_correct:
        st.session_state["logged_in"] = True
        st.session_state["role"] = user_role_dari_db # Simpan role di sini
        return True
    return False

def sidebar_logout():
    if st.session_state.login_sukses:
        st.sidebar.divider()
        if st.sidebar.button("Logout"):
            st.session_state.login_sukses = False
            st.rerun()
