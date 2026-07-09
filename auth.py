import streamlit as st

def tampilkan_sidebar():
    with st.sidebar:
        st.title("Sistem Gudang")
        
        if st.session_state.get("logged_in", False):
            st.divider()
            # Menu yang hanya muncul saat sudah login
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.session_state["current_page"] = "login"
                st.rerun()
        else:
            # Menu saat belum login
            if st.button("Ke Halaman Login"):
                st.session_state["current_page"] = "login"
                st.rerun()
