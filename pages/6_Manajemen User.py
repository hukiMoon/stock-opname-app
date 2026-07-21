import streamlit as st
import pandas as pd
import bcrypt
from db_utils import jalankan_query, jalankan_perintah_db
from utils import check_login, tampilkan_sidebar, card_container

st.set_page_config(page_title="Manajemen User - Stock Opname Setum Polri", page_icon="👥", layout="wide")

# 1. Proteksi Halaman & Tampilkan Sidebar
check_login()
tampilkan_sidebar()

# 2. Proteksi Ganda: Pastikan hanya admin yang bisa mengakses halaman ini
if st.session_state.get("role") != "admin":
    st.error("Akses Ditolak. Halaman ini hanya untuk Admin.")
    st.stop()

st.title("👥 Manajemen User")
st.write("---")

# --- BAGIAN 1: TAMPILKAN DATA USER ---
st.subheader("Daftar Pengguna Sistem")
# Mengambil data user tanpa mengambil password_hash demi keamanan
data_users = jalankan_query("SELECT id, username, role FROM users ORDER BY id ASC")

if data_users:
    df_users = pd.DataFrame(data_users, columns=["ID User", "Username", "Role / Peran"])
    st.dataframe(df_users, hide_index=True, use_container_width=True)
else:
    st.info("Belum ada data user.")

st.write("---")

# Membagi layar menjadi 3 kolom untuk Tambah, Hapus, dan Ubah Password
col1, col2, col3 = st.columns(3)

# --- BAGIAN 2: TAMBAH USER BARU (Kolom 1) ---
with col1:
    with card_container("Tambah User Baru"):
        with st.form("form_tambah_user", clear_on_submit=True):
            new_username = st.text_input("Username Baru").strip()
            new_password = st.text_input("Password", type="password").strip()
            new_role = st.selectbox("Role / Peran", ["staff", "admin"])
            
            submit_tambah = st.form_submit_button("Simpan User", type="primary", use_container_width=True)
            
            if submit_tambah:
                if not new_username or not new_password:
                    st.error("Username dan Password tidak boleh kosong!")
                else:
                    cek_user = jalankan_query("SELECT username FROM users WHERE username = %s", (new_username,))
                    if cek_user:
                        st.error(f"Username '{new_username}' sudah ada.")
                    else:
                        salt = bcrypt.gensalt()
                        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
                        jalankan_perintah_db(
                            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", 
                            (new_username, hashed_pw, new_role)
                        )
                        st.success(f"User '{new_username}' ditambahkan!")
                        st.rerun()

# --- BAGIAN 3: HAPUS USER (Kolom 2) ---
with col2:
    with card_container("Hapus User"):
        if data_users:
            daftar_pilihan = [f"{u[0]} - {u[1]}" for u in data_users]
            pilih_hapus = st.selectbox("Pilih User", daftar_pilihan, key="select_hapus")
            
            id_hapus = pilih_hapus.split(" - ")[0]
            username_hapus = pilih_hapus.split(" - ")[1]
            
            st.caption(f"⚠️ Hapus akun **{username_hapus}** secara permanen.")
            
            if st.button("Hapus Permanen", use_container_width=True):
                jalankan_perintah_db("DELETE FROM users WHERE id = %s", (id_hapus,))
                st.success(f"User '{username_hapus}' berhasil dihapus!")
                st.rerun()
        else:
            st.info("Tidak ada data.")

# --- BAGIAN 4: UBAH PASSWORD (Kolom 3) ---
with col3:
    with card_container("Ubah Password"):
        if data_users:
            with st.form("form_ubah_password", clear_on_submit=True):
                # Membuat daftar pilihan yang sama seperti pada fitur Hapus
                daftar_pilihan = [f"{u[0]} - {u[1]}" for u in data_users]
                # Menambahkan parameter 'key' agar Streamlit tidak bingung membedakan dengan selectbox di kolom Hapus
                pilih_ubah = st.selectbox("Pilih User", daftar_pilihan, key="select_ubah")
                
                # Input untuk kata sandi baru
                password_baru = st.text_input("Password Baru", type="password").strip()
                
                submit_ubah = st.form_submit_button("Simpan Password", type="primary", use_container_width=True)
                
                if submit_ubah:
                    if not password_baru:
                        st.error("Password baru tidak boleh kosong!")
                    else:
                        id_ubah = pilih_ubah.split(" - ")[0]
                        username_ubah = pilih_ubah.split(" - ")[1]
                        
                        # Mengamankan password baru
                        salt = bcrypt.gensalt()
                        hashed_pw = bcrypt.hashpw(password_baru.encode('utf-8'), salt).decode('utf-8')
                        
                        # Memperbarui password di database
                        jalankan_perintah_db(
                            "UPDATE users SET password_hash = %s WHERE id = %s", 
                            (hashed_pw, id_ubah)
                        )
                        st.success(f"Password '{username_ubah}' berhasil diubah!")
                        st.rerun()
        else:
            st.info("Tidak ada data.")
