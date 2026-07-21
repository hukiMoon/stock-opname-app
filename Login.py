import streamlit as st
import setup_db
from utils import init_login_state, show_login

# 1. Konfigurasi halaman dasar
st.set_page_config(
    page_title="Login - Stock Opname", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. EKSEKUSI CSS PALING AWAL: 
# Memaksa sidebar hilang tanpa menunggu elemen form login dimuat
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Inisialisasi database
setup_db.inisialisasi_user_awal()

# 4. Inisialisasi state login
init_login_state()

# 5. Logika Pengalihan Halaman
if not st.session_state["logged_in"]:
    show_login()
else:
    st.switch_page("pages/0_Beranda.py")
