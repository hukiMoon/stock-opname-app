import streamlit as st
import setup_db
from utils import init_login_state, show_login, tampilkan_sidebar

setup_db.inisialisasi_user_awal()

# Konfigurasi halaman
st.set_page_config(page_title="Aplikasi Stock Opname", layout="wide")

init_login_state()

if st.session_state["logged_in"]:
    if "role" in st.session_state and st.session_state["role"]:
        role = st.session_state["role"].capitalize()
        st.title(f"Hallo, Selamat datang {role}!")
        tampilkan_sidebar()
    else:
        st.title("Selamat Datang di Sistem Inventaris Gudang")
        st.info("Silakan login untuk mengakses fitur penuh.")
else:
    show_login()

# 1. Inisialisasi status login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
