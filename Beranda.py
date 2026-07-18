import streamlit as st
import setup_db
import pandas as pd
from utils import init_login_state, show_login, tampilkan_sidebar
from db_utils import jalankan_query

# 1. Inisialisasi
setup_db.inisialisasi_user_awal()
st.set_page_config(page_title="Aplikasi Stock Opname", layout="wide")
init_login_state()

# 2. Logika Utama (Satu Alur)
if not st.session_state["logged_in"]:
    # Jika belum login, tampilkan layar login saja
    show_login()
else:
    # Jika sudah login, tampilkan konten dashboard
    tampilkan_sidebar()
    role = st.session_state.get("role", "User").capitalize()
    
    st.title(f"Hallo, Selamat datang {role}! 👋")
    st.markdown("---")

    # --- Ringkasan Operasional ---
    with st.container():
        st.subheader("Ringkasan Operasional")
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Total Barang", value="150")
        col2.metric(label="Barang Masuk (Hari ini)", value="25")
        with col3.container(border=True):
            st.metric(label="⚠️ Stok Kritis", value="3", delta="Perlu Tindakan", delta_color="inverse")

    st.markdown("---")
    
    # --- Visualisasi ---
    st.subheader("📊 Visualisasi Stok Barang")
    query_grafik = "SELECT nama_barang, stok_sistem FROM barang LIMIT 10"
    data = jalankan_query(query_grafik)

    if data:
        df = pd.DataFrame(data, columns=['Nama Barang', 'Stok'])
        df = df.set_index('Nama Barang')
        st.bar_chart(df)
    else:
        st.info("Belum ada data barang untuk ditampilkan di grafik.")

    # --- Akses Cepat ---
    st.markdown("---")
    left_col, right_col = st.columns([2, 1])
    with left_col:
        st.subheader("Informasi Terkini")
        st.write("Aplikasi ini digunakan untuk memantau arus barang keluar-masuk gudang secara real-time.")
    with right_col:
        st.subheader("Akses Cepat")
        st.button("Input Barang Masuk")
        st.button("Laporan Stok")
