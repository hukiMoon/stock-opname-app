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
    
    # Menu untuk Semua Pengguna (jika sudah login)
    st.sidebar.page_link("Beranda.py", label="🏠 Beranda")
    
    # Menu khusus Admin
    if st.session_state.get("role") == "admin":
        st.sidebar.divider()
        st.sidebar.subheader("Menu Admin")
        
        # Tambahkan SEMUA halaman Anda di sini
        st.sidebar.page_link("pages/1_📥_Barang_Masuk.py", label="📥 Barang Masuk")
        st.sidebar.page_link("pages/2_📥_Barang_Keluar.py", label="📥 Barang Keluar")
        st.sidebar.page_link("pages/3_📜_Riwayat_Log.py", label="📜 Riwayat Log")
        st.sidebar.page_link("pages/4_⚙️_Master_Barang.py", label="⚙️ Master Barang")
        st.sidebar.page_link("pages/5_📈_Statistik.py", label="📈 Statistik")
        # Tambahkan baris untuk setiap file di folder pages Anda di bawah ini
        # st.sidebar.page_link("pages/nama_file_lain.py", label="Nama Menu")
    
    st.sidebar.divider()
    
    # Tombol Logout (muncul untuk semua yang sudah login)
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
