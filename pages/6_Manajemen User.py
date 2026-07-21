import streamlit as st
import pandas as pd
import bcrypt
from db_utils import jalankan_query, jalankan_perintah_db
from utils import check_login, tampilkan_sidebar, card_container

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
# Kita mengambil data user, tapi TIDAK mengambil password_hash demi keamanan
data_users = jalankan_query("SELECT id, username, role FROM users ORDER BY id ASC")

if data_users:
    # Memasukkan data ke dalam tabel rapi
    df_users = pd.DataFrame(data_users, columns=["ID User", "Username", "Role / Peran"])
    st.dataframe(df_users, hide_index=True, use_container_width=True)
else:
    st.info("Belum ada data user.")

st.write("---")

# Membagi layar menjadi 2 kolom untuk form Tambah dan Hapus
col1, col2 = st.columns(2)

# --- BAGIAN 2: TAMBAH USER BARU ---
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
                    # Mengecek apakah username sudah pernah didaftarkan
                    cek_user = jalankan_query("SELECT username FROM users WHERE username = %s", (new_username,))
                    if cek_user:
                        st.error(f"Username '{new_username}' sudah digunakan. Silakan pilih yang lain.")
                    else:
                        # Enkripsi password menggunakan bcrypt agar aman di database
                        salt = bcrypt.gensalt()
                        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
                        
                        # Menyimpan user baru ke database
                        jalankan_perintah_db(
                            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", 
                            (new_username, hashed_pw, new_role)
                        )
                        st.success(f"User '{new_username}' berhasil ditambahkan!")
                        st.rerun() # Refresh halaman untuk melihat data terbaru

# --- BAGIAN 3: HAPUS USER ---
with col2:
    with card_container("Hapus User"):
        if data_users:
            # Membuat format pilihan dropdown: "ID - Username"
            daftar_pilihan = [f"{u[0]} - {u[1]}" for u in data_users]
            pilih_hapus = st.selectbox("Pilih User untuk Dihapus", daftar_pilihan)
            
            # Memisahkan string untuk mengambil ID user-nya saja
            id_hapus = pilih_hapus.split(" - ")[0]
            username_hapus = pilih_hapus.split(" - ")[1]
            
            # Peringatan kecil
            st.caption(f"⚠️ Hati-hati, aksi ini akan menghapus akun **{username_hapus}** secara permanen.")
            
            if st.button("Hapus Permanen", use_container_width=True):
                # Menghapus user berdasarkan ID
                jalankan_perintah_db("DELETE FROM users WHERE id = %s", (id_hapus,))
                st.success(f"User '{username_hapus}' berhasil dihapus!")
                st.rerun() # Refresh halaman
        else:
            st.info("Tidak ada data untuk dihapus.")
