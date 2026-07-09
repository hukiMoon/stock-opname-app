import streamlit as st

# HAPUS baris 'from db_utils import jalankan_query' dari bagian atas!

def form_login():
    # Pindahkan import ke dalam fungsi (Lazy Import)
    from db_utils import jalankan_query 
    
    st.subheader("Login ke Aplikasi")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Masuk"):
        # Contoh penggunaan jalankan_query
        # user = jalankan_query("SELECT ... WHERE username = ?", (username,))
        
        # Simulasi validasi (ganti dengan hasil query database Anda)
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "admin"
            st.rerun()
        else:
            st.error("Username atau password salah!")

def tampilkan_sidebar():
    st.sidebar.title("Menu Utama")
    
    # Navigasi ke Halaman Beranda (Selalu ada)
    st.sidebar.page_link("Beranda.py", label="🏠 Beranda")
    
    # Navigasi khusus Admin
    if st.session_state.get("role") == "admin":
        st.sidebar.divider()
        st.sidebar.subheader("Menu Admin")
        st.sidebar.page_link("pages/4_⚙️_Master_Barang.py", label="⚙️ Manajemen Master")
        # Tambahkan page_link lainnya di sini
    
    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
