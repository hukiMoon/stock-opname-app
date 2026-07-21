import streamlit as st
import setup_db
from utils import init_login_state, show_login

# 1. Konfigurasi halaman dasar (Tambahkan initial_sidebar_state="collapsed")
st.set_page_config(
    page_title="Login - Stock Opname", 
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# 2. Inisialisasi database (menjalankan setup user pertama kali jika belum ada)
setup_db.inisialisasi_user_awal()

# 3. Inisialisasi state login
init_login_state()

# 4. Logika Pengalihan Halaman
if not st.session_state["logged_in"]:
    # Jika belum login, tampilkan form login
    show_login()
else:
    # Jika sudah login, langsung alihkan ke halaman Beranda
    st.switch_page("pages/0_Beranda.py")
