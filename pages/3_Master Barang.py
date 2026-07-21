import streamlit as st
import init_path # Pastikan ini ada
from db_utils import jalankan_query
from utils import check_login, tampilkan_sidebar, card_container

st.set_page_config(page_title="Master Barang - Stock Opname Setum Polri", page_icon="⚙️", layout="wide")

check_login()
tampilkan_sidebar()

st.title("⚙️ Manajemen Master Data")
st.write("---")

# Ambil data barang
daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY kode_barang ASC")
daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []

with card_container("Kelola Barang"):
    if not daftar_barang:
        st.info("Belum ada data barang.")
    else:
        aksi = st.radio("Pilih Tindakan:", ["Edit Nama Barang", "Hapus Barang Permanen"], horizontal=True)
        
        if aksi == "Edit Nama Barang":
            pilihan_barang = st.selectbox("Pilih Barang:", daftar_barang)
            nama_terpilih = pilihan_barang.split(" - ")[1]
            nama_baru = st.text_input("Nama Baru:", value=nama_terpilih).strip().upper()
                
            if st.button("Simpan Perubahan Nama", type="primary"):
                if nama_baru and nama_baru != nama_terpilih:
                    # Update kedua tabel
                    jalankan_query("UPDATE barang SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, nama_terpilih), commit=True)
                    jalankan_query("UPDATE riwayat SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, nama_terpilih), commit=True)
                    st.success(f"Berhasil mengubah {nama_terpilih} menjadi {nama_baru}")
                    st.rerun()

        else: # Hapus Barang
            pilihan_barang = st.selectbox("Pilih Barang Dihapus:", daftar_barang)
            kd_hapus = pilihan_barang.split(" - ")[0]
            
            st.warning(f"Anda akan menghapus permanen: **{pilihan_barang}**")
            if st.checkbox("Saya mengerti, hapus barang beserta seluruh riwayatnya."):
                if st.button("Hapus Permanen", type="primary"):
                    # Cek apakah ada riwayat
                    # Hapus riwayat dulu untuk menghindari error foreign key
                    jalankan_query("DELETE FROM riwayat WHERE kode_barang = %s", (kd_hapus,), commit=True)
                    jalankan_query("DELETE FROM barang WHERE kode_barang = %s", (kd_hapus,), commit=True)
                    st.success("Barang dan riwayat terkait berhasil dihapus!")
                    st.rerun()
