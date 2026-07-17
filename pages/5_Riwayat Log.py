import streamlit as st
import pandas as pd
import init_path # Pastikan ini ada
from db_utils import jalankan_query, ambil_riwayat_terfilter
from utils import check_login, tampilkan_sidebar, card_container

check_login()
tampilkan_sidebar()

st.title("📜 Log Aktivitas Gudang")
st.write("---")

# Filter UI
with st.expander("🔍 Filter Pencarian Canggih", expanded=True):
    col1, col2, col3, col4 = st.columns(4) # Menambah kolom untuk layout
    with col1:
        nama_cari = st.text_input("Cari Nama Barang")
    with col2:
        jenis_pilih = st.multiselect("Jenis Transaksi", ["MASUK", "KELUAR"])
    with col3:
        # Menambahkan input untuk sub-bagian/tujuan
        sub_pilih = st.selectbox("Sub Bagian/Tujuan", [None, "SUBBAGRENMIN", "SUBBAGTAKAH", "SUBBAGBINSET", "SUBBAGARSIP", "SUBBAGUM", "KANPOS", "URKEU"])
    with col4:
        tgl_awal = st.date_input("Dari Tanggal", value=pd.to_datetime("2026-01-01"))
        tgl_akhir = st.date_input("Sampai Tanggal")

if st.button("Cari Data"):
    # Memanggil fungsi dengan parameter tambahan
    data = ambil_riwayat_terfilter(nama_cari, jenis_pilih, tgl_awal, tgl_akhir, sub_pilih)
    
    if data:
        df = pd.DataFrame(data, columns=["Kode Barang", "Nama Barang", "Jenis Transaksi", "Jumlah", "Satuan", "Tanggal", "Keterangan"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Data tidak ditemukan.")
