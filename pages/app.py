import streamlit as st
import Login

# Mengatur konfigurasi halaman
st.set_page_config(page_title="Sistem Gudang", layout="wide")

# Inisialisasi status login jika belum ada
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Logika kontrol akses
if not st.session_state["logged_in"]:
    # Jika belum login, tampilkan halaman Login
    Login.show_login()
else:
    # Jika sudah login, tampilkan navigasi ke fitur lainnya
    st.sidebar.title("Navigasi Menu")
    
    # Contoh navigasi (sesuaikan dengan nama filemu)
    menu = st.sidebar.radio("Pilih Halaman:", ["Statistik", "Barang Masuk", "Barang Keluar"])
    
    if menu == "Statistik":
        import 1_Statistik.py
    elif menu == "Barang Masuk":
        import 2_Barang_Masuk
    
    # Tombol Logout
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()
