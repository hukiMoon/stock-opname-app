import streamlit as st
from utils import check_login, tampilkan_sidebar
from db_utils import update_password_user

# 1. Proteksi halaman (wajib login)
check_login()

# 2. Tampilkan sidebar navigasi
tampilkan_sidebar()

st.title("🔒 Ubah Kata Sandi")
st.write("Gunakan formulir di bawah ini untuk memperbarui kata sandi akunmu.")
st.markdown("---")

# Ambil username dari session_state yang sedang aktif
username_aktif = st.session_state.get("username") 
# (Pastikan saat login sukses sebelumnya, kamu juga menyimpan st.session_state["username"] = username)

with st.form("form_ubah_password"):
    password_lama = st.text_input("Password Lama", type="password")
    password_baru = st.text_input("Password Baru", type="password")
    konfirmasi_password = st.text_input("Konfirmasi Password Baru", type="password")
    
    submit_btn = st.form_submit_button("Simpan Password Baru", use_container_width=True)
    
    if submit_btn:
        if not password_lama or not password_baru or not konfirmasi_password:
            st.error("Semua kolom wajib diisi!")
        elif password_baru != konfirmasi_password:
            st.error("Konfirmasi password baru tidak cocok!")
        elif len(password_baru) < 5:
            st.warning("Password baru terlalu pendek (minimal 5 karakter).")
        else:
            # Panggil fungsi update password
            sukses, pesan = update_password_user(username_aktif, password_lama, password_baru)
            if sukses:
                st.success(pesan)
            else:
                st.error(pesan)
