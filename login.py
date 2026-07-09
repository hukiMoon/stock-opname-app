import streamlit as st

def show_login():
    st.title("🔐 Login ke Aplikasi")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Masuk")
        
        if submit:
            if username == "admin" and password == "admin123":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Username atau Password salah")
