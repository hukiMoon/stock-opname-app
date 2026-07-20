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
        st.warning("Silakan login terlebih dahulu.")
        # Opsi: arahkan ke beranda atau tampilkan form login
        st.stop()

def check_role(required_role):
    """Fungsi proteksi tambahan untuk memeriksa peran (role) pengguna."""
    # Jika role pengguna saat ini bukan admin DAN bukan role yang diminta, maka akses ditolak
    if st.session_state.get("role") != required_role and st.session_state.get("role") != "admin":
        st.error("⛔ Anda tidak memiliki akses untuk membuka halaman manajemen ini.")
        st.stop()

def show_login():
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Masuk")

        if submit_button:
            role = autentikasi_user(username, password) # Fungsi dari db_utils[span_4](start_span)[span_4](end_span)
            if role:
                st.session_state["logged_in"] = True
                st.session_state["role"] = role
                st.rerun() # Hanya rerun sekali setelah state diperbarui
            else:
                st.error("Username atau password salah!")

def logout():
    """Fungsi untuk keluar dari sistem dengan membersihkan seluruh state."""
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    # Bersihkan state lain jika ada
    st.rerun()

def tampilkan_sidebar():
    with st.sidebar:
        st.title("📦 Menu Gudang")
        
        # 1. Pastikan user sudah login
        if "role" not in st.session_state or not st.session_state.get("role"):
            st.warning("Silakan login terlebih dahulu.")
            return

        role = st.session_state["role"]
        st.write(f"Login sebagai: **{role.upper()}**")
        st.markdown("---")

        st.write("**Pilih Menu:**")
        
        # 2. Tampilkan navigasi menggunakan st.page_link
        # Beranda.py tetap tanpa folder karena berada di luar
        st.page_link("Beranda.py", label="Beranda", icon="🏠")

        # 3. Tambahkan menu berdasarkan Role pengguna
        if role == "admin":
            st.page_link("pages/1_Barang Masuk.py", label="Barang Masuk", icon="📥")
            st.page_link("pages/2_Barang Keluar.py", label="Barang Keluar", icon="📤")
            st.page_link("pages/3_Master Barang.py", label="Master Barang", icon="⚙️")
            st.page_link("pages/4_Riwayat Log.py", label="Riwayat Log", icon="📜")
            st.page_link("pages/5_Laporan.py", label="Laporan", icon="📊")
            
        elif role == "staff":
            st.page_link("pages/1_Barang Masuk.py", label="Barang Masuk", icon="📥")
            st.page_link("pages/5_Laporan.py", label="Laporan", icon="📜")

        st.markdown("---")
        
        # 4. Tombol Logout
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.rerun()

# 1. Fungsi untuk membuat tampilan kartu (card) yang Anda butuhkan
def card_container(title):
    st.subheader(title)
    return st.container(border=True)

# 2. Fungsi untuk gaya/styling (misalnya pesan sukses/error yang seragam)
def tampilkan_pesan_sukses(pesan):
    st.success(f"✅ {pesan}")

# 3. Fungsi format angka (agar tampilan mata uang lebih rapi)
def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

# 4. Fungsi bantu lainnya (misalnya untuk reset state)
def reset_input():
    st.session_state["input_reset"] = True
