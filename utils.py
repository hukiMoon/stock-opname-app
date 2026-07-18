import streamlit as st
import bcrypt
from db_utils import jalankan_query
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
        st.subheader("Login Sistem")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Masuk")

        if submit_button:
            # Panggil fungsi autentikasi baru
            role = autentikasi_user(username, password)
            if role:
                st.session_state["logged_in"] = True
                st.session_state["role"] = role # Simpan role ke session
                st.rerun() 
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

        # 2. Definisikan navigasi dasar yang bisa dilihat semua orang
        menu_opsi = ["Beranda", "Statistik"]
        
        # 3. Tambahkan menu berdasarkan Role
        if role == "admin":
            menu_opsi.extend(["Barang Masuk", "Laporan", "Manajemen User"])
        elif role == "staff":
            menu_opsi.extend(["Barang Masuk", "Laporan"])

        # 4. Tampilkan menu radio
        pilihan = st.radio("Pilih Menu:", menu_opsi)
        
        st.markdown("---")
        
        # 5. Tombol Logout
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.rerun()

    return pilihan

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
