import streamlit as st
import psycopg2
from datetime import datetime

DB_URL = "postgresql://postgres.krckbruwpxgiziujgqiy:1P%40ny001%2E%2E%2E@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

def jalankan_query(sql, param=(), commit=False):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute(sql, param)
    data = None
    if not commit: data = cursor.fetchall()
    else: conn.commit()
    conn.close()
    return data

def generate_kode_otomatis():
    data = jalankan_query("SELECT id FROM barang ORDER BY id DESC LIMIT 1")
    return f"STM-{(data[0][0] + 1):02d}" if data else "STM-01"

if st.query_params.get("session") != "loggedin":
    st.warning("Silakan login terlebih dahulu di halaman utama!")
else:
    st.title("📥 Input Barang Masuk")
    st.write("---")
    
    opsi_input = st.radio("Pilih Jenis Input:", ["Barang Baru (Belum Terdaftar)", "Tambah Stok Barang Lama"])
    
    if opsi_input == "Barang Baru (Belum Terdaftar)":
        with st.form("form_masuk_baru", clear_on_submit=True):
            kode_otomatis = generate_kode_otomatis()
            st.info(f"📋 **Kode Barang Baru Otomatis:** {kode_otomatis}")
            nama_barang = st.text_input("Nama Barang Baru:").strip().upper()
            satuan_barang = st.selectbox("Pilih Satuan:", ["PCS", "SET", "RIM", "BOX", "PACK"])
            jumlah_masuk = st.number_input("Jumlah Barang Masuk:", min_value=1, step=1)
            tanggal_pilihan = st.date_input("Tanggal Masuk:")
            input_keterangan = st.text_input("Keterangan:").strip()
            
            if st.form_submit_button("Simpan Transaksi Masuk", use_container_width=True):
                if nama_barang:
                    jalankan_query("INSERT INTO barang (kode_barang, nama_barang, stok_sistem, satuan) VALUES (%s, %s, %s, %s)", (kode_otomatis, nama_barang, jumlah_masuk, satuan_barang), commit=True)
                    jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'MASUK', %s, %s, %s, %s)", (kode_otomatis, nama_barang, jumlah_masuk, satuan_barang, tanggal_pilihan.strftime("%Y-%m-%d"), input_keterangan), commit=True)
                    st.success("Barang baru tersimpan!")
                    st.rerun()
    else:
        daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY LENGTH(kode_barang) ASC, kode_barang ASC")
        daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []
        
        if not daftar_barang:
            st.info("Belum ada data barang lama.")
        else:
            pilihan_barang = st.selectbox("Pilih Barang:", daftar_barang)
            nama_barang = pilihan_barang.split(" - ")[1]
            kd_brg, stok_sekarang, satuan_tampil = jalankan_query("SELECT kode_barang, stok_sistem, satuan FROM barang WHERE nama_barang = %s", (nama_barang,))[0]
            
            with st.form(f"form_masuk_lama_{nama_barang.replace(' ', '_')}", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1: st.text_input("Stok Tersedia Saat Ini:", value=f"{stok_sekarang} {satuan_tampil}", disabled=True)
                with col2: jumlah_masuk = st.number_input("Jumlah Barang Masuk:", min_value=1, step=1)
                tanggal_pilihan = st.date_input("Tanggal Masuk:")
                input_keterangan = st.text_input("Keterangan:").strip()
                
                if st.form_submit_button("Simpan Tambah Stok", use_container_width=True):
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_sekarang + jumlah_masuk, nama_barang), commit=True)
                    jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'MASUK', %s, %s, %s, %s)", (kd_brg, nama_barang, jumlah_masuk, satuan_tampil, tanggal_pilihan.strftime("%Y-%m-%d"), input_keterangan), commit=True)
                    st.success("Stok berhasil ditambahkan!")
                    st.rerun()
