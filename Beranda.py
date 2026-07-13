import streamlit as st
from utils import init_login_state, show_login, tampilkan_sidebar

# Konfigurasi halaman
st.set_page_config(page_title="Aplikasi Stock Opname", layout="wide")

init_login_state()

if st.session_state["logged_in"]:
    st.write("Selamat datang di sistem!")
    tampilkan_sidebar()
else:
    show_login()

# 1. Inisialisasi status login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 2. Definisikan fungsi login
#def show_login():
    #st.subheader("🔐 Silakan Login")
    
    #with st.form("login_form"):
        #username = st.text_input("Username")
        #password = st.text_input("Password", type="password")
        #submit_button = st.form_submit_button("Masuk")
        
        #if submit_button:
            # Ganti dengan logika verifikasi database Anda di masa depan
            #if username == "98010786" and password == "1P@ny001":
                #st.session_state["logged_in"] = True
                #st.success("Login Berhasil!")
                #st.rerun() 
            #else:
                #st.error("Username atau Password salah!")

# 3. Logika kontrol akses
#if not st.session_state["logged_in"]:
    # Cukup panggil fungsi secara langsung
    #show_login()
#else:
    # Jika sudah login, tampilkan menu utama/sidebar
    #st.title("💻 Halo! Selamat datang Admin.")
    #st.write("---")
    #st.sidebar.title("Navigasi Menu")
    #st.sidebar.success("Anda berhasil login!")
    
    #if st.sidebar.button("Logout"):
        #st.session_state["logged_in"] = False
        #st.rerun()
