import streamlit as st
import psycopg2

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

if st.query_params.get("session") != "loggedin":
    st.warning("Silakan login terlebih dahulu di halaman utama!")
else:
    st.title("⚙️ Manajemen Master Data")
    st.write("---")
    
    daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY LENGTH(kode_barang) ASC, kode_barang ASC")
    daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []
    
    if not daftar_barang:
        st.info("Belum ada data barang.")
    else:
        aksi = st.radio("Pilih Tindakan:", ["Edit Nama Barang", "Hapus Barang Permanen"], horizontal=True)
        
        if aksi == "Edit Nama Barang":
            pilihan_barang = st.selectbox("Pilih Barang:", daftar_barang)
            nama_terpilih = pilihan_barang.split(" - ")[1]
            nama_baru = st.text_input("Nama Baru:", value=nama_terpilih).strip().upper()
            
            if st.button("Simpan Perubahan Nama", use_container_width=True):
                if nama_baru and nama_baru != nama_terpilih:
                    jalankan_query("UPDATE barang SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, nama_terpilih), commit=True)
                    jalankan_query("UPDATE riwayat SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, nama_terpilih), commit=True)
                    st.success("Berhasil diubah!")
                    st.rerun()
        else:
            pilihan_barang = st.selectbox("Pilih Barang Dihapus:", daftar_barang)
            nama_hapus = pilihan_barang.split(" - ")[1]
            st.warning(f"Menghapus permanen: {pilihan_barang}")
            if st.checkbox("Saya setuju menghapus data ini."):
                if st.button("Hapus Permanen", type="primary", use_container_width=True):
                    jalankan_query("DELETE FROM barang WHERE nama_barang = %s", (nama_hapus,), commit=True)
                    st.success("Barang dihapus!")
                    st.rerun()
