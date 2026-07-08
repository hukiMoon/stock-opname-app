import streamlit as st
import pandas as pd
from datetime import datetime
from auth import check_password, sidebar_logout
from db_utils import jalankan_query

check_password()
sidebar_logout()

st.title("📜 Log Aktivitas Gudang")
st.write("---")
    
data_riwayat = jalankan_query("SELECT kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan FROM riwayat ORDER BY id DESC")
if not data_riwayat:
    st.info("Belum ada riwayat transaksi.")
else:
    df = pd.DataFrame(data_riwayat, columns=["Kode Barang", "Nama Barang", "Jenis Transaksi", "Jumlah", "Satuan", "Tanggal Transaksi", "Keterangan"])
    st.dataframe(df, hide_index=True, use_container_width=True)
