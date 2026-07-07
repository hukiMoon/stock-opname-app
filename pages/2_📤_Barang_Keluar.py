import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

DB_URL = "postgresql://postgres.krckbruwpxgiziujgqiy:1P%40ny001%2E%2E%2E@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

def jalankan_query(sql, param=(), commit=False):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute(sql, param)
    data = cursor.fetchall() if not commit else None
    if commit: conn.commit()
    conn.close()
    return data

st.title("📤 Input Barang Keluar")
st.write("---")

daftar_db = jalankan_query("SELECT kode_barang, nama_barang, stok_sistem, satuan FROM barang WHERE stok_sistem > 0")
daftar_barang = [f"{b[0]} - {b[1]} (Stok: {b[2]} {b[3]})" for b in daftar_db] if daftar_db else []

if not daftar_barang:
    st.warning("Tidak ada barang dengan stok tersedia.")
else:
    pilihan = st.selectbox("Pilih Barang:", daftar_barang)
    nama_brg = pilihan.split(" - ")[1].split(" (")[0]
    data_brg = jalankan_query("SELECT kode_barang, stok_sistem, satuan FROM barang WHERE nama_barang = %s", (nama_brg,))[0]
    
    with st.form("form_keluar", clear_on_submit=True):
        st.write(f"Stok saat ini: {data_brg[1]} {data_brg[2]}")
        jml_keluar = st.number_input("Jumlah Keluar:", min_value=1, max_value=data_brg[1], step=1)
        tgl = st.date_input("Tanggal Keluar:")
        ket = st.text_input("Tujuan/Keterangan:")
        
        if st.form_submit_button("Simpan Transaksi Keluar"):
            jalankan_query("UPDATE barang SET stok_sistem = stok_sistem - %s WHERE nama_barang = %s", (jml_keluar, nama_brg), commit=True)
            jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'KELUAR', %s, %s, %s, %s)", (data_brg[0], nama_brg, jml_keluar, data_brg[2], tgl.strftime("%Y-%m-%d"), ket if ket else "-"), commit=True)
            st.success("Stok berhasil dikurangi!")
            st.rerun()
