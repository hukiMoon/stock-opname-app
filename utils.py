import streamlit as st
import bcrypt
from db_utils import jalankan_query

def init_login_state():
    """Memastikan variabel sesi login selalu terinisialisasi."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

def check_login():
    """Fungsi proteksi untuk memastikan pengguna sudah login."""
    init_login_state() # Pastikan state ada
    if not st.session_state["logged_in"]:
        st.warning("Silakan login terlebih dahulu.")
        st.stop()

def check_role(required_role):
    """Fungsi proteksi tambahan untuk memeriksa peran (role) pengguna."""
    # Jika role pengguna saat ini bukan admin DAN bukan role yang diminta, maka akses ditolak
    if st.session_state.get("role") != required_role and st.session_state.get("role") != "admin":
        st.error("⛔ Anda tidak memiliki akses untuk membuka halaman manajemen ini.")
        st.stop()

def show_login():
    st.subheader("🔐 Silakan Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Masuk")
        
        if submit_button:
            # Ambil data user dari DB
            data = jalankan_query("SELECT password_hash, role FROM users WHERE username = %s", (username,))
            
            if data:
                hashed_db = data[0][0].encode('utf-8')
                role_db = data[0][1]
                
                # Cek apakah password cocok
                if bcrypt.checkpw(password.encode('utf-8'), hashed_db):
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = role_db
                    st.rerun()
                else:
                    st.error("Password salah!")
            else:
                st.error("Username tidak ditemukan!")

def logout():
    """Fungsi untuk keluar dari sistem."""
    st.session_state["logged_in"] = False
    st.rerun()

def tampilkan_sidebar():
    st.sidebar.title("Navigasi Menu")
    st.sidebar.success("Anda berhasil login!")
    
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun() # Refresh halaman untuk kembali ke layar login

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
