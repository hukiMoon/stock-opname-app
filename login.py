# login.py
import streamlit as st

def show_login():
    # Menggunakan container agar tampilan lebih bersih
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # Membuat layout kolom untuk memusatkan form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login ke Aplikasi")
        st.write("Silakan masukkan kredensial Anda")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Masuk")
            
            if submit:
                # Logika validasi (Ganti dengan pengecekan database Anda nanti)
                if username == "admin" and password == "admin123":
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = "admin"
                    st.rerun()
                else:
                    st.error("Username atau password salah!")
