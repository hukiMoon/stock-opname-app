import streamlit as st
import psycopg2
from datetime import datetime

# ==========================================
# GANTI DENGAN CONNECTION STRING SUPABASE-MU
# ==========================================
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

if "loggedin" not in st.session_state or not st.session_state["loggedin"]:
    st.warning("⚠️ Silakan login terlebih dahulu di halaman utama (app.py)!")
else:
    st.title("📤 Input Barang Keluar")
    st.write("---")
    
    # Ambil data barang urut berdasarkan kode
    daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY LENGTH(kode_barang) ASC, kode_barang ASC")
    daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []
    
    if not daftar_barang:
        st.info("Belum ada data barang di sistem.")
    else:
        pilihan_barang = st.selectbox("Pilih Barang Keluar:", daftar_barang)
        nama_barang = pilihan_barang.split(" - ")[1]
        kd_brg, stok_sekarang, sat_brg = jalankan_query("SELECT kode_barang, stok_sistem, satuan FROM barang WHERE nama_barang = %s", (nama_barang,))[0]
        
        # Form dinamis di-lock berdasarkan nama barang agar cache segar
        with st.form(f"form_keluar_{nama_barang.replace(' ', '_')}", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: 
                st.text_input("Stok Tersedia Saat Ini:", value=f"{stok_sekarang} {sat_brg}", disabled=True)
            with col2: 
                jumlah_keluar = st.number_input("Jumlah Barang Keluar:", min_value=1, step=1)
            
            # Peringatan real-time jika overstock out
            if jumlah_keluar > stok_sekarang:
                st.warning(f"⚠️ **Peringatan:** Jumlah melebihi stok tersedia!")
                
            tanggal_keluar = st.date_input("Tanggal Keluar:", value=datetime.now().date())
            
            # --- TAMBAHAN DROPDOWN PILIHAN SUB BAGIAN ---
            tujuan_subbag = st.selectbox(
                "Tujuan Pengeluaran / Sub Bagian:", 
                ["SUBBAGRENMIN", "SUBBAGTAKAH", "SUBBAGBINSET", "SUBBAGARSIP", "SUBBAGUM", "KANPOS", "URKEU"]
            )
            
            input_catatan = st.text_input("Catatan Tambahan (Opsional):", placeholder="Contoh: Keperluan cetak dokumen / Nama penerima").strip()
            
            if st.form_submit_button("Simpan Transaksi Keluar", use_container_width=True):
                if jumlah_keluar > stok_sekarang:
                    st.error("Gagal! Stok tidak mencukupi.")
                else:
                    # Gabungkan info Sub Bagian dan Catatan Tambahan untuk disimpan ke kolom keterangan database
                    keterangan_final = f"Tujuan: {tujuan_subbag}"
                    if input_catatan:
                        keterangan_final += f" ({input_catatan})"
                        
                    # Potong stok di tabel master barang
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_sekarang - jumlah_keluar, nama_barang), commit=True)
                    
                    # Catat log transaksi masuk ke tabel riwayat
                    jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'KELUAR', %s, %s, %s, %s)", 
                                   (kd_brg, nama_barang, jumlah_keluar, sat_brg, tanggal_keluar.strftime("%Y-%m-%d"), keterangan_final), commit=True)
                    
                    st.success(f"Transaksi keluar untuk {tujuan_subbag} berhasil disimpan!")
                    st.rerun()
