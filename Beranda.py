import streamlit as st
import setup_db
from utils import tampilkan_sidebar

setup_db.inisialisasi_user_awal()

# Konfigurasi halaman
st.set_page_config(page_title="Aplikasi Stock Opname", layout="wide")

if "role" in st.session_state and st.session_state["role"]:
    role = st.session_state["role"].capitalize()
    st.title(f"Hallo, Selamat datang {role}!👋")
    tampilkan_sidebar()
else:
    st.title("Sistem Inventaris Gudang")
    
st.markdown("---")

# Menggunakan Container untuk ringkasan
with st.container():
    st.subheader("Ringkasan Operasional")
    
    # Membuat 3 kolom untuk statistik
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Barang", value="150", delta="12")
    with col2:
        st.metric(label="Barang Masuk (Hari ini)", value="25", delta="5")
    with col3:
        st.metric(label="Stok Kritis", value="3", delta="Perlu Perhatian", delta_color="inverse")

st.markdown("---")

# Menggunakan kolom untuk membagi info tambahan
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Informasi Terkini")
    st.write("Aplikasi ini digunakan untuk memantau arus barang keluar-masuk gudang secara real-time.")
    
with right_col:
    st.subheader("Akses Cepat")
    st.button("Input Barang Masuk")
    st.button("Laporan Stok")
