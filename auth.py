import streamlit as st

def form_login():
    # Pindahkan import ke dalam fungsi (Lazy Import)
    from db_utils import jalankan_query 
    
    st.subheader("Login ke Aplikasi")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Masuk"):
        # Simulasi validasi (ganti dengan hasil query database Anda)
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "admin"
            st.rerun()
        else:
            st.error("Username atau password salah!")

def cek_akses_admin():
    """Fungsi untuk memproteksi halaman admin."""
    if st.session_state.get("role") != "admin":
        st.error("⚠️ Anda tidak memiliki akses ke halaman ini!")
        st.stop()

def tampilkan_sidebar():
    # Cek apakah user sudah login di session_state
    if st.session_state.get("logged_in", False):
        with st.sidebar:
            st.title("Menu Utama")
            # ... (kode menu Anda di sini)
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()
    else:
        # Jika belum login, sidebar tidak memuat menu (kosong)
        pass

def check_role():
    if st.session_state.get("role") != "admin":
        st.error("⚠️ Anda tidak memiliki akses ke halaman ini!")
        st.stop()
