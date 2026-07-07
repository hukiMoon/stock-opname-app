import streamlit as st
import psycopg2
import pandas as pd
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
    
    daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY LENGTH(kode_barang) ASC, kode_barang ASC")
    daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []
    
    if not daftar_barang:
        st.info("Belum ada data barang di sistem.")
    else:
        pilihan_barang = st.selectbox("Pilih Barang Keluar:", daftar_barang)
        nama_barang = pilihan_barang.split(" - ")[1]
        kd_brg, stok_sekarang, sat_brg = jalankan_query("SELECT kode_barang, stok_sistem, satuan FROM barang WHERE nama_barang = %s", (nama_barang,))[0]
        
        with st.form(f"form_keluar_{nama_barang.replace(' ', '_')}", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: st.text_input("Stok Tersedia Saat Ini:", value=f"{stok_sekarang} {sat_brg}", disabled=True)
            with col2: jumlah_keluar = st.number_input("Jumlah Barang Keluar:", min_value=1, step=1)
            
            if jumlah_keluar > stok_sekarang:
                st.warning(f"⚠️ **Peringatan:** Jumlah melebihi stok tersedia!")
                
            tanggal_keluar = st.date_input("Tanggal Keluar:", value=datetime.now().date())
            tujuan_subbag = st.selectbox("Tujuan Pengeluaran / Sub Bagian:", ["SUBBAGRENMIN", "SUBBAGTAKAH", "SUBBAGBINSET", "SUBBAGARSIP", "SUBBAGUM", "KANPOS", "URKEU"])
            input_catatan = st.text_input("Catatan Tambahan (Opsional):").strip()
            
            if st.form_submit_button("Simpan Transaksi Keluar", use_container_width=True):
                if jumlah_keluar > stok_sekarang:
                    st.error("Gagal! Stok tidak mencukupi.")
                else:
                    keterangan_final = f"Tujuan: {tujuan_subbag}" + (f" ({input_catatan})" if input_catatan else "")
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_sekarang - jumlah_keluar, nama_barang), commit=True)
                    jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'KELUAR', %s, %s, %s, %s)", (kd_brg, nama_barang, jumlah_keluar, sat_brg, tanggal_keluar.strftime("%Y-%m-%d"), keterangan_final), commit=True)
                    st.success("Transaksi keluar berhasil!")
                    st.rerun()

    # --- TABEL RIWAYAT + FITUR EDIT & DELETE ---
    st.write("---")
    st.subheader("📜 Riwayat Khusus Barang Keluar")
    st.caption("💡 *Klik ganda untuk mengedit Jumlah/Keterangan. Pilih baris lalu klik ikon Tong Sampah atau tekan Delete untuk menghapus.*")
    
    raw_riwayat = jalankan_query("SELECT id, kode_barang, nama_barang, jumlah, tanggal, keterangan FROM riwayat WHERE jenis_transaksi = 'KELUAR' ORDER BY id DESC")
    
    if not raw_riwayat:
        st.info("Belum ada riwayat transaksi keluar.")
    else:
        df_riwayat = pd.DataFrame(raw_riwayat, columns=["ID Transaksi", "Kode Barang", "Nama Barang", "Jumlah", "Tanggal", "Keterangan/Tujuan"])
        
        edited_df = st.data_editor(
            df_riwayat,
            disabled=["ID Transaksi", "Kode Barang", "Nama Barang", "Tanggal"],
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            key="editor_keluar"
        )
        
        if st.button("SINKRONISASI PERUBAHAN & PENGHAPUSAN KELUAR", type="primary", use_container_width=True):
            # 1. Logika Hapus Baris
            set_id_sekarang = set(edited_df["ID Transaksi"].tolist())
            for baris in raw_riwayat:
                id_asal = baris[0]
                if id_asal not in set_id_sekarang:
                    nm_b, jml_lama = baris[2], baris[3]
                    # Kembalikan stok ke master barang karena pengeluaran dibatalkan
                    stok_skrg = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nm_b,))[0][0]
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_skrg + jml_lama, nm_b), commit=True)
                    jalankan_query("DELETE FROM riwayat WHERE id = %s", (id_asal,), commit=True)
            
            # 2. Logika Edit Baris
            for _, row in edited_df.iterrows():
                id_cek = row["ID Transaksi"]
                jml_baru = int(row["Jumlah"])
                ket_baru = str(row["Keterangan/Tujuan"])
                
                data_lama = [b for b in raw_riwayat if b[0] == id_cek][0]
                jml_lama = data_lama[3]
                nm_b = data_lama[2]
                
                if jml_baru != jml_lama or ket_baru != data_lama[5]:
                    selisih = jml_baru - jml_lama
                    stok_skrg = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nm_b,))[0][0]
                    # Update master barang (dikurangi karena ini barang keluar) & log riwayat
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_skrg - selisih, nm_b), commit=True)
                    jalankan_query("UPDATE riwayat SET jumlah = %s, keterangan = %s WHERE id = %s", (jml_baru, ket_baru, id_cek), commit=True)
            
            st.success("Perubahan riwayat keluar berhasil disimpan!")
            st.rerun()
