import streamlit as st
import bcrypt
import extra_streamlit_components as stx
from db_utils import jalankan_query, autentikasi_user
from setup_db import inisialisasi_user_awal

# PERBAIKAN: Berikan key unik pada CookieManager agar tidak terjadi duplikasi elemen
@st.cache_resource
def get_manager():
    return stx.CookieManager(key="cookie_manager_gudang_app")

cookie_manager = get_manager()

def init_login_state():
    """Memastikan variabel sesi login selalu terinisialisasi dan tersinkronisasi dengan cookie."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "role" not in st.session_state:
        st.session_state["role"] = None

    # Cek apakah session kosong tapi cookie tersimpan (artinya baru di-refresh)
    if not st.session_state["logged_in"]:
        try:
            cookie_login = cookie_manager.get(cookie="gudang_logged_in")
            cookie_role = cookie_manager.get(cookie="gudang_role")
            
            if cookie_login == "True" and cookie_role:
                st.session_state["logged_in"] = True
                st.session_state["role"] = cookie_role
        except Exception:
            pass # Mencegah error saat cookie belum siap dibaca pada render pertama

def check_login():
    """Fungsi proteksi untuk memastikan pengguna sudah login (mendukung cookie)."""
    init_login_state()
    if not st.session_state.get("logged_in") or not st.session_state.get("role"):
        st.switch_page("Login.py")

def logout():
    """Fungsi untuk keluar dari sistem, menghapus cookie, dan kembali ke halaman Login."""
    try:
        cookie_manager.delete("gudang_logged_in")
        cookie_manager.delete("gudang_role")
    except Exception:
        pass
    
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    
    st.switch_page("Login.py")
        
def show_login():
    # 1. CSS untuk menyembunyikan sidebar
    sembunyikan_sidebar = """
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="collapsedControl"] { display: none; }
        </style>
    """
    st.markdown(sembunyikan_sidebar, unsafe_allow_html=True)
    
    kolom_kiri, kolom_tengah, kolom_kanan = st.columns([1, 2, 1])
    
    with kolom_tengah:
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        st.write("---")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Masuk", use_container_width=True)

            if submit_button:
                role = autentikasi_user(username, password)
                if role:
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = role
                    
                    # PERBAIKAN: Menggunakan blok try-except untuk mencegah error crash pada cookie manager
                    try:
                        cookie_manager.set("gudang_logged_in", "True", max_age=86400)
                        cookie_manager.set("gudang_role", role, max_age=86400)
                    except Exception:
                        pass
                    
                    st.rerun()
                else:
                    st.error("Username atau password salah!")

def tampilkan_sidebar():
    with st.sidebar:
        # --- 1. CSS BERSIH DAN STABIL ---
        pengaturan_tampilan = """
            <style>
                /* 1. Menghilangkan daftar halaman otomatis bawaan Streamlit */
                div[data-testid="stSidebarNav"] {
                    display: none !important;
                }
                
                /* 2. Menghapus ruang kosong di area header sidebar */
                div[data-testid="stSidebarHeader"] {
                    padding: 0rem !important;
                    height: 0rem !important;
                    min-height: 0rem !important;
                }
                
                /* 3. Memaksa pembungkus utama sidebar untuk menempel ke atas */
                section[data-testid="stSidebar"] > div:first-child {
                    padding-top: 1.5rem !important; 
                }
                
                /* 4. Menghilangkan jarak (margin) bawaan dari st.title */
                section[data-testid="stSidebar"] h1 {
                    padding-top: 1rem !important; 
                    margin-top: 0rem !important;
                }
            </style>
        """
        st.markdown(pengaturan_tampilan, unsafe_allow_html=True)
        # -------------------------------------------------------------------

        st.title("📦 Menu Gudang")
        
        # 2. Pastikan user sudah login
        if "role" not in st.session_state or not st.session_state.get("role"):
            st.warning("Silakan login terlebih dahulu.")
            return

        role = st.session_state["role"]
        st.write(f"Login sebagai: **{role.upper()}**")
        st.markdown("---")

        st.write("**Pilih Menu:**")
        
        # 3. Tampilkan navigasi buatan kita menggunakan st.page_link
        st.page_link("pages/0_Beranda.py", label="Beranda", icon="🏠")

        # 4. Tambahkan menu berdasarkan Role pengguna
        if role == "admin":
            st.page_link("pages/1_Barang Masuk.py", label="Barang Masuk", icon="📥")
            st.page_link("pages/2_Barang Keluar.py", label="Barang Keluar", icon="📤")
            st.page_link("pages/3_Master Barang.py", label="Master Barang", icon="⚙️")
            st.page_link("pages/4_Riwayat Log.py", label="Riwayat Log", icon="📜")
            st.page_link("pages/5_Laporan.py", label="Laporan", icon="📊")
            st.page_link("pages/6_Manajemen User.py", label="Manajemen User", icon="👥")
            
        elif role == "staff":
            st.page_link("pages/1_Barang Masuk.py", label="Barang Masuk", icon="📥")
            st.page_link("pages/5_Laporan.py", label="Laporan", icon="📜")

        st.markdown("---")
        
        # 5. Tombol Logout
        if st.button("Logout"):
            from utils import logout
            logout()

# 1. Fungsi untuk membuat tampilan kartu (card) yang Anda butuhkan
def card_container(title):
    st.subheader(title)
    return st.container(border=True)

# 2. Fungsi untuk gaya/styling (misalnya pesan sukses/error yang seragam)
def tampilkan_pesan_sukses(pesan):
    st.success(f"✅ {pesan}")

# 3. Fungsi format angka (agar tampilan mata uang lebih rapi)
def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

# 4. Fungsi bantu lainnya (misalnya untuk reset state)
def reset_input():
    st.session_state["input_reset"] = True
