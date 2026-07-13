import streamlit as st
import Login # Pastikan Login.py berada di folder utama yang sama dengan app.py

# Konfigurasi halaman
st.set_page_config(page_title="Aplikasi Stock Opname", layout="wide")

# Inisialisasi status login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Logika kontrol akses
if not st.session_state["logged_in"]:
    # Jika belum login, tampilkan halaman Login
    Login.show_login()
else:
    # Jika sudah login, Streamlit akan otomatis menampilkan 
    # file yang ada di folder 'pages/' di sidebar.
    st.sidebar.title("Navigasi Menu")
    st.sidebar.success("Anda berhasil login!")
    
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()
