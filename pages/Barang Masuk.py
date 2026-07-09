import streamlit as st
import pandas as pd
from db_utils import jalankan_query, get_data_barang
from auth import cek_akses_admin, tampilkan_sidebar

if st.session_state.get("role") != "admin":
    st.error("Anda tidak memiliki akses ke halaman ini!")
    st.stop()

# Pastikan user sudah login
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("auth.py") # Arahkan ke halaman login jika belum login

# Jika sudah login, tampilkan sidebar
tampilkan_sidebar()

st.title("📥 Input Barang Masuk")
st.write("Selamat datang, Anda telah login!")

opsi_input = st.radio("Pilih Jenis Input:", ["Barang Baru (Belum Terdaftar)", "Tambah Stok Barang Lama"])

# --- FORM INPUT ---
data = get_data_barang(st.session_state.get("role"))

#st.dataframe(data)

if opsi_input == "Barang Baru (Belum Terdaftar)":
    with st.form("form_masuk_baru", clear_on_submit=True):
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

# --- TABEL RIWAYAT ---
st.write("---")
st.subheader("📜 Riwayat Khusus Barang Masuk")
raw_riwayat = jalankan_query("SELECT id, kode_barang, nama_barang, jumlah, tanggal, keterangan FROM riwayat WHERE jenis_transaksi = 'MASUK' ORDER BY id DESC")

if not raw_riwayat:
    st.info("Belum ada riwayat transaksi masuk.")
else:
    df_riwayat = pd.DataFrame(raw_riwayat, columns=["ID Transaksi", "Kode Barang", "Nama Barang", "Jumlah", "Tanggal", "Keterangan"])
    
    st.write("🔍 **Filter Riwayat:**")
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search_query = st.text_input("Cari Kode / Nama Barang:", placeholder="Ketik kata kunci...", key="search_masuk").strip().upper()
    with col_f2:
        filter_date = st.date_input("Filter Berdasarkan Tanggal:", value=None, key="date_masuk")
    
    if search_query:
        df_riwayat = df_riwayat[df_riwayat["Nama Barang"].str.contains(search_query, na=False) | df_riwayat["Kode Barang"].str.contains(search_query, na=False)]
    if filter_date:
        df_riwayat = df_riwayat[df_riwayat["Tanggal"] == filter_date.strftime("%Y-%m-%d")]
        
    edited_df = st.data_editor(df_riwayat, disabled=["ID Transaksi", "Kode Barang", "Nama Barang", "Tanggal"], num_rows="dynamic", hide_index=True, use_container_width=True, key="editor_masuk")
    
    if st.button("SINKRONISASI PERUBAHAN & PENGHAPUSAN MASUK", type="primary", use_container_width=True):
        set_id_sekarang = set(edited_df["ID Transaksi"].tolist())
        id_terlihat = df_riwayat["ID Transaksi"].tolist()
        
        for baris in raw_riwayat:
            id_asal = baris[0]
            if id_asal in id_terlihat and id_asal not in set_id_sekarang:
                nm_b, jml_lama = baris[2], baris[3]
                stok_skrg = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nm_b,))[0][0]
                jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (max(0, stok_skrg - jml_lama), nm_b), commit=True)
                jalankan_query("DELETE FROM riwayat WHERE id = %s", (id_asal,), commit=True)
        
        for _, row in edited_df.iterrows():
            id_cek = row["ID Transaksi"]
            jml_baru = int(row["Jumlah"])
            ket_baru = str(row["Keterangan"])
            data_lama = [b for b in raw_riwayat if b[0] == id_cek][0]
            if jml_baru != data_lama[3] or ket_baru != data_lama[5]:
                selisih = jml_baru - data_lama[3]
                stok_skrg = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (data_lama[2],))[0][0]
                jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_skrg + selisih, data_lama[2]), commit=True)
                jalankan_query("UPDATE riwayat SET jumlah = %s, keterangan = %s WHERE id = %s", (jml_baru, ket_baru, id_cek), commit=True)
        st.success("Perubahan riwayat berhasil!")
        st.rerun()
