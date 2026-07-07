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
    st.title("📥 Input Barang Masuk")
    st.write("---")
    
    opsi_input = st.radio("Pilih Jenis Input:", ["Barang Baru (Belum Terdaftar)", "Tambah Stok Barang Lama"])
    
    # --- FORM INPUT ---
    if opsi_input == "Barang Baru (Belum Terdaftar)":
        with st.form("form_masuk_baru", clear_on_submit=True):
            # Generate otomatis kode
            data_kd = jalankan_query("SELECT id FROM barang ORDER BY id DESC LIMIT 1")
            kode_otomatis = f"STM-{(data_kd[0][0] + 1):02d}" if data_kd else "STM-01"
            
            st.info(f"📋 **Kode Barang Baru Otomatis:** {kode_otomatis}")
            nama_barang = st.text_input("Nama Barang Baru:").strip().upper()
            satuan_barang = st.selectbox("Pilih Satuan:", ["PCS", "SET", "RIM", "BOX", "PACK"])
            jumlah_masuk = st.number_input("Jumlah Barang Masuk:", min_value=1, step=1)
            tanggal_pilihan = st.date_input("Tanggal Masuk:")
            input_keterangan = st.text_input("Keterangan:").strip()
            
            if st.form_submit_button("Simpan Transaksi Masuk", use_container_width=True):
                if nama_barang:
                    jalankan_query("INSERT INTO barang (kode_barang, nama_barang, stok_sistem, satuan) VALUES (%s, %s, %s, %s)", (kode_otomatis, nama_barang, jumlah_masuk, satuan_barang), commit=True)
                    jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'MASUK', %s, %s, %s, %s)", (kode_otomatis, nama_barang, jumlah_masuk, satuan_barang, tanggal_pilihan.strftime("%Y-%m-%d"), input_keterangan if input_keterangan else "-"), commit=True)
                    st.success("Barang baru berhasil didaftarkan!")
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
                    jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'MASUK', %s, %s, %s, %s)", (kd_brg, nama_barang, jumlah_masuk, satuan_tampil, tanggal_pilihan.strftime("%Y-%m-%d"), input_keterangan if input_keterangan else "-"), commit=True)
                    st.success("Stok berhasil ditambahkan!")
                    st.rerun()

    # --- TABEL RIWAYAT + FITUR EDIT & DELETE ---
    st.write("---")
    st.subheader("📜 Riwayat Khusus Barang Masuk")
    st.caption("💡 *Klik ganda pada kotak Jumlah/Keterangan untuk Edit. Pilih baris lalu tekan tombol Delete pada keyboard untuk menghapus.*")
    
    raw_riwayat = jalankan_query("SELECT id, kode_barang, nama_barang, jumlah, tanggal, keterangan FROM riwayat WHERE jenis_transaksi = 'MASUK' ORDER BY id DESC")
    
    if not raw_riwayat:
        st.info("Belum ada riwayat transaksi masuk.")
    else:
        df_riwayat = pd.DataFrame(raw_riwayat, columns=["ID Transaksi", "Kode Barang", "Nama Barang", "Jumlah", "Tanggal", "Keterangan"])
        
        # Tampilkan editor data
        edited_df = st.data_editor(
            df_riwayat,
            disabled=["ID Transaksi", "Kode Barang", "Nama Barang", "Tanggal"],
            num_rows="dynamic", # Mengaktifkan tombol hapus baris bawaan streamlit
            hide_index=True,
            use_container_width=True,
            key="editor_masuk"
        )
        
        # Deteksi Aksi Simpan Perubahan
        if st.button("SINKRONISASI PERUBAHAN & PENGHAPUSAN MASUK", type="primary", use_container_width=True):
            # 1. Cek Data yang Dihapus
            set_id_sekarang = set(edited_df["ID Transaksi"].tolist())
            for baris in raw_riwayat:
                id_asal = baris[0]
                if id_asal not in set_id_sekarang: # Artinya baris ini dihapus user
                    kd_b, nm_b, jml_lama = baris[1], baris[2], baris[3]
                    # Kurangi stok master barang karena transaksi masuknya dibatalkan
                    stok_skrg = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nm_b,))
                    if stok_skrg:
                        stok_baru = max(0, stok_skrg[0][0] - jml_lama)
                        jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nm_b), commit=True)
                    jalankan_query("DELETE FROM riwayat WHERE id = %s", (id_asal,), commit=True)
            
            # 2. Cek Data yang Diedit Jumlah atau Keterangannya
            for _, row in edited_df.iterrows():
                id_cek = row["ID Transaksi"]
                jml_baru = int(row["Jumlah"])
                ket_baru = str(row["Keterangan"])
                
                # Ambil nilai lama dari database awal sebelum diedit
                data_lama = [b for b in raw_riwayat if b[0] == id_cek][0]
                jml_lama = data_lama[3]
                nm_b = data_lama[2]
                
                if jml_baru != jml_lama or ket_baru != data_lama[5]:
                    selisih = jml_baru - jml_lama
                    stok_skrg = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nm_b,))[0][0]
                    # Update master barang & log riwayat
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_skrg + selisih, nm_b), commit=True)
                    jalankan_query("UPDATE riwayat SET jumlah = %s, keterangan = %s WHERE id = %s", (jml_baru, ket_baru, id_cek), commit=True)
            
            st.success("Perubahan riwayat masuk berhasil disimpan!")
            st.rerun()
