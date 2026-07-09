import streamlit as st

def form_login():
    # Pindahkan import ke dalam fungsi (Lazy Import)
    from db_utils import jalankan_query 
    
    st.subheader("Login ke Aplikasi")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Masuk"):
        # Simulasi validasi (ganti dengan hasil query database Anda)
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "admin"
            st.rerun()
        else:
            st.error("Username atau password salah!")

def cek_akses_admin():
    """Fungsi untuk memproteksi halaman admin."""
    if st.session_state.get("role") != "admin":
        st.error("⚠️ Anda tidak memiliki akses ke halaman ini!")
        st.stop()

def tampilkan_sidebar():
    with st.sidebar:
        if st.session_state.get("logged_in", False):
            # MENU ADMIN (Jika sudah login)
            st.title("Menu Utama")
            st.page_link("Beranda.py", label="Beranda", icon="🏠")
            st.page_link("pages/Barang_Masuk.py", label="Barang Masuk", icon="📥")
            # ... tambahkan menu lainnya ...
            
            st.divider()
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()
        else:
            # MENU LOGIN (Jika belum login)
            st.title("Sistem Gudang")
            st.info("Silakan login untuk mengakses menu.")
            # Ini akan mengarahkan user kembali ke halaman utama (Login)
            if st.button("Halaman Login"):
                st.switch_page("Beranda.py")
            
def check_role():
    if st.session_state.get("role") != "admin":
        st.error("⚠️ Anda tidak memiliki akses ke halaman ini!")
        st.stop()
