import streamlit as st

# Mengatur tampilan halaman agar rapi
st.set_page_config(page_title="Login", layout="centered")

def show_login():
    # Menghapus padding/header bawaan agar lebih bersih
    st.markdown("""
        <style>
        .block-container { padding-top: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔐 Silakan Login")
    
    # Menggunakan form agar lebih terstruktur
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Tombol login saja
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            # Logika autentikasi Anda di sini
            if username == "admin" and password == "admin":
                st.session_state["logged_in"] = True
                st.session_state["role"] = "admin"
                st.success("Login Berhasil!")
                st.rerun()
            else:
                st.error("Username atau Password salah")

# Panggil fungsi login
if not st.session_state.get("logged_in", False):
    login_page()
else:
    st.write("Anda sudah login.")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()
