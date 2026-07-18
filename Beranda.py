import streamlit as st
import setup_db
import pandas as pd
from utils import init_login_state, show_login, tampilkan_sidebar
from db_utils import jalankan_query

setup_db.inisialisasi_user_awal()

# Konfigurasi halaman
st.set_page_config(page_title="Aplikasi Stock Opname", layout="wide")

init_login_state()
pilihan = tampilkan_sidebar()

if pilihan == "Beranda":
    st.switch_page("Beranda.py")
elif pilihan == "Statistik":
    st.switch_page("pages/1_Statistik.py")
elif pilihan == "Barang Masuk":
    st.switch_page("pages/2_Barang Masuk.py")
elif pilihan == "Laporan":
    st.switch_page("pages/6_Laporan.py")

if st.session_state["logged_in"]:
    if "role" in st.session_state and st.session_state["role"]:
        role = st.session_state["role"].capitalize()
        st.title(f"Hallo, Selamat datang {role}!👋")

        st.markdown("---")

        # Menggunakan Container untuk ringkasan
        with st.container():
            st.subheader("Ringkasan Operasional")
    
        # Membuat 3 kolom untuk statistik
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="Total Barang", value="150")

        with col2:
            st.metric(label="Barang Masuk (Hari ini)", value="25")

        # Bagian Stok Kritis dibuat lebih menonjol
        with col3:
            # Kita menggunakan st.container dengan border (fitur baru Streamlit)
            # untuk memberikan efek "kartu" yang mencolok
            with st.container(border=True):
                st.metric(
                    label="⚠️ Stok Kritis", 
                    value="3", 
                    delta="Perlu Tindakan", 
                    delta_color="inverse"
                )

        st.markdown("---")
        st.subheader("📊 Visualisasi Stok Barang")

        # 1. Mengambil data untuk grafik dari database
        # Asumsi tabelmu bernama 'barang' dan memiliki kolom 'nama_barang' dan 'stok'
        query_grafik = "SELECT nama_barang, stok_sistem FROM barang LIMIT 10"
        data = jalankan_query(query_grafik)

        # 2. Mengubah hasil query menjadi format yang bisa dibaca grafik (DataFrame)
        if data:
            df = pd.DataFrame(data, columns=['Nama Barang', 'Stok'])
            df = df.set_index('Nama Barang') # Mengatur nama barang sebagai label
    
            # 3. Menampilkan grafik batang
            st.bar_chart(df)
        else:
            st.info("Belum ada data barang untuk ditampilkan di grafik.")

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
    else:
        st.title("Sistem Inventaris Gudang")
else:
    show_login()
