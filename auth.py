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
    
    # ... navigasi Anda ...
    
    st.sidebar.divider()
    
    # Tombol Logout
    if st.sidebar.button("Logout"):
        # 1. Hapus semua data di session state
        st.session_state.clear() 
        
        # 2. Atau jika ingin spesifik, set ulang key Anda:
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        
        # 3. Wajib: rerun agar aplikasi kembali ke state awal (login)
        st.rerun()
