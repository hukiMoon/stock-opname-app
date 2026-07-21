import streamlit as st
import pandas as pd
import plotly.express as px
from utils import check_login, tampilkan_sidebar
from db_utils import jalankan_query, get_ringkasan_kpi, get_stok_rendah 
from pdf_utils import export_to_pdf

# 1. Konfigurasi halaman
st.set_page_config(page_title="Beranda - Stock Opname", page_icon="🏠", layout="wide")

# 2. Proteksi Halaman & Tampilkan Sidebar
# check_login() akan memaksa user kembali/berhenti jika belum login
check_login()
tampilkan_sidebar()

# 3. Logika Utama Beranda
role = st.session_state.get("role", "User").capitalize()

st.title(f"Hallo, Selamat datang {role}! 👋")
st.markdown("Ringkasan pergerakan stok dan status barang saat ini.")
st.markdown("---")

# --- Mengambil Data ---
# Mengambil total jenis barang dari tabel master
kpi_data = get_ringkasan_kpi()

# Mengambil data riwayat transaksi
data_riwayat = jalankan_query("SELECT jenis_transaksi, jumlah, tanggal, nama_barang FROM riwayat")

if not data_riwayat:
    st.info("Belum ada data transaksi untuk ditampilkan di dashboard.")
else:
    # Memasukkan data ke Pandas DataFrame
    df = pd.DataFrame(data_riwayat, columns=["Jenis Transaksi", "Jumlah", "Tanggal", "Nama Barang"])
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # Mengubah semua teks transaksi menjadi huruf kapital agar seragam (MASUK / KELUAR)
    df["Jenis Transaksi"] = df["Jenis Transaksi"].str.upper()

    # Menghitung total masuk dan keluar
    total_masuk = df[df["Jenis Transaksi"] == "MASUK"]["Jumlah"].sum()
    total_keluar = df[df["Jenis Transaksi"] == "KELUAR"]["Jumlah"].sum()
    
    # --- Ringkasan Operasional (Disesuaikan menjadi 4 kolom) ---
    st.subheader("📦 Ringkasan Operasional")
    col1, col2, col3, col4 = st.columns(4)
    
    # Menambahkan metrik Total Jenis Barang dari fitur sebelumnya
    col1.metric("Total Jenis Barang", kpi_data["total_barang"]) 
    col2.metric("Total Barang Masuk", total_masuk)
    col3.metric("Total Barang Keluar", total_keluar)
    col4.metric("Sisa Stok (Estimasi)", total_masuk - total_keluar)

    st.markdown("---")
    
    # --- Peringatan Stok Menipis (Tambahan Fitur Baru) ---
    st.subheader("⚠️ Peringatan Stok Menipis")
    batas_minimum = 10  # Angka peringatan stok (bisa disesuaikan)
    stok_rendah = get_stok_rendah(batas_minimum)

    if stok_rendah:
        # PERBAIKAN: Menambahkan "Satuan" ke dalam daftar nama kolom
        df_stok_rendah = pd.DataFrame(stok_rendah, columns=["Nama Barang", "Sisa Stok", "Satuan"])
        
        # Mengubah nomor urut (index) agar dimulai dari 1
        df_stok_rendah.index = df_stok_rendah.index + 1
        
        st.dataframe(df_stok_rendah, use_container_width=True)
        st.warning(f"Terdapat {len(stok_rendah)} barang dengan stok di bawah atau sama dengan {batas_minimum}!")
    else:
        st.success(f"Semua stok barang dalam kondisi aman (Di atas {batas_minimum} unit).")

    st.markdown("---")
    
    # --- Visualisasi Data Gudang (Kode Aslimu) ---
    st.subheader("📈 Visualisasi Data Gudang")
    
    # Tombol Download PDF
    st.download_button(
        label="📥 Download Laporan Statistik (PDF)",
        data=export_to_pdf(df),
        file_name="Laporan_Statistik_Dashboard.pdf",
        mime="application/pdf"
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grafik Tren Aktivitas Bulanan
    df_trend = df.groupby([df["Tanggal"].dt.to_period("M"), "Jenis Transaksi"])["Jumlah"].sum().reset_index()
    df_trend["Tanggal_Str"] = df_trend["Tanggal"].astype(str)
    
    fig1 = px.line(
        df_trend, 
        x="Tanggal_Str", 
        y="Jumlah", 
        color="Jenis Transaksi", 
        title="Tren Aktivitas Bulanan", 
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Grafik Top 5 Barang Keluar
    st.markdown("<br>", unsafe_allow_html=True)
    df_top = df[df["Jenis Transaksi"] == "KELUAR"].groupby("Nama Barang")["Jumlah"].sum().nlargest(5).reset_index()
    fig2 = px.bar(
        df_top, 
        x="Jumlah", 
        y="Nama Barang", 
        orientation='h', 
        title="Top 5 Barang Paling Sering Keluar", 
        color="Jumlah"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Akses Cepat (Kode Aslimu) ---
st.markdown("---")
left_col, right_col = st.columns([2, 1])
with left_col:
    st.subheader("Informasi Terkini")
    st.write("Aplikasi ini digunakan untuk memantau arus barang keluar-masuk gudang secara real-time.")
with right_col:
    st.subheader("Akses Cepat")
    st.page_link("pages/1_Barang Masuk.py", label="Input Barang Masuk", icon="📥")
    st.page_link("pages/5_Laporan.py", label="Lihat Laporan Stok", icon="📊")
