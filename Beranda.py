import streamlit as st
import setup_db
from utils import init_login_state, show_login, tampilkan_sidebar

setup_db.inisialisasi_user_awal()

# Konfigurasi halaman
st.set_page_config(page_title="Aplikasi Stock Opname", layout="wide")
st.title("Selamat Datang di Sistem Inventaris Gudang")
st.write("Silakan pilih menu di sidebar untuk mulai bekerja.")

init_login_state()

if st.session_state["logged_in"]:
    st.title("💻 Halo! Selamat datang Admin.")
    st.write("---")
    tampilkan_sidebar()
else:
    show_login()

# 1. Inisialisasi status login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
