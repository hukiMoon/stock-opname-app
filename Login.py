import streamlit as st

def show_login():
    # Menggunakan container untuk memusatkan tampilan
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("🔐 Silakan Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Tombol submit
        submit_button = st.form_submit_button("Masuk")
        
        if submit_button:
            # Ganti 'admin' dengan username/password yang Anda inginkan
            if username == "admin" and password == "admin123":
                st.session_state["logged_in"] = True
                st.success("Login Berhasil!")
                st.rerun() # Refresh halaman untuk menampilkan konten utama
            else:
                st.error("Username atau Password salah!")
