import streamlit as st
import bcrypt
from db_utils import jalankan_query, autentikasi_user
from setup_db import inisialisasi_user_awal

def init_login_state():
    """Memastikan variabel sesi login selalu terinisialisasi."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "role" not in st.session_state:
        st.session_state["role"] = None

def check_login():
    """Fungsi proteksi untuk memastikan pengguna sudah login."""
    init_login_state()
    if not st.session_state.get("logged_in") or not st.session_state.get("role"):
        st.switch_page("Login.py")

def show_login():
    # 1. CSS untuk menyembunyikan sidebar dan tombol panah
    sembunyikan_sidebar = """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="collapsedControl"] {
                display: none;
            }
        </style>
    """
    st.markdown(sembunyikan_sidebar, unsafe_allow_html=True)
    
    kolom_kiri, kolom_tengah, kolom_kanan = st.columns([1, 2, 1])
    
    with kolom_tengah:
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        st.write("---")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Masuk", use_container_width=True)

            if submit_button:
                role = autentikasi_user(username, password)
                if role:
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = role
                    st.rerun()
                else:
                    st.error("Username atau password salah!")

# 1. Buat fungsi dialog konfirmasi logout
@st.dialog("Konfirmasi Logout")
def dialog_konfirmasi_logout():
    st.write("Apakah Anda yakin ingin keluar dari sistem?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ya, Logout", use_container_width=True, type="primary"):
            # Proses pembersihan sesi
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.session_state.pop("username", None) # Bersihkan username jika ada
            st.rerun()
            st.switch_page("Login.py")
            
    with col2:
        if st.button("Batal", use_container_width=True):
            st.rerun() # Menutup dialog dan kembali normal
            
def tampilkan_sidebar():
    with st.sidebar:
        # --- 1. CSS UNTUK TAMPILAN SIDEBAR ---
        pengaturan_tampilan = """
            <style>
                /* 1. Menghilangkan daftar halaman otomatis */
                div[data-testid="stSidebarNav"] {
                    display: none !important;
                }
                
                /* 2. Menghapus ruang kosong di area header sidebar */
                div[data-testid="stSidebarHeader"] {
                    padding: 0rem !important;
                    height: 0rem !important;
                    min-height: 0rem !important;
                }
                
                /* 3. Memaksa pembungkus utama sidebar untuk menempel ke atas */
                section[data-testid="stSidebar"] > div:first-child {
                    padding-top: 1.5rem !important; 
                }
                
                /* 4. Menghilangkan jarak (margin) bawaan dari st.title */
                section[data-testid="stSidebar"] h1 {
                    padding-top: 1rem !important; 
                    margin-top: 0rem !important;
                }
            </style>
        """
        st.markdown(pengaturan_tampilan, unsafe_allow_html=True)
        # -------------------------------------------------------------------

        st.title("📦 Aplikasi Persediaan Setum Polri")
        
        if "role" not in st.session_state or not st.session_state.get("role"):
            st.warning("Silakan login terlebih dahulu.")
            return

        role = st.session_state["role"]
        st.write(f"Login sebagai: **{role.upper()}**")
        st.markdown("---")

        st.write("**Pilih Menu:**")
        
        st.page_link("pages/0_Beranda.py", label="Beranda", icon="🏠")

        if role == "admin":
            st.page_link("pages/1_Barang Masuk.py", label="Barang Masuk", icon="📥")
            st.page_link("pages/2_Barang Keluar.py", label="Barang Keluar", icon="📤")
            st.page_link("pages/3_Master Barang.py", label="Master Barang", icon="⚙️")
            st.page_link("pages/4_Riwayat Log.py", label="Riwayat Log", icon="📜")
            st.page_link("pages/5_Laporan.py", label="Laporan", icon="📊")
            st.page_link("pages/6_Manajemen User.py", label="Manajemen User", icon="👥")
            st.page_link("pages/7_Ubah Password.py", label="Ubah Password", icon="🔑")
            
        elif role == "staff":
            st.page_link("pages/1_Barang Masuk.py", label="Barang Masuk", icon="📥")
            st.page_link("pages/5_Laporan.py", label="Laporan", icon="📜")
            st.page_link("pages/7_Ubah Password.py", label="Ubah Password", icon="🔑")

        st.markdown("---")
        
        # Mengubah tombol logout biasa menjadi pemanggil dialog konfirmasi
        if st.button("Logout", use_container_width=True):
            dialog_konfirmasi_logout()

def card_container(title):
    st.subheader(title)
    return st.container(border=True)
