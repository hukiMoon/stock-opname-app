import pandas as pd
import io
import psycopg2
import psycopg2.extras
import streamlit as st
import bcrypt
from contextlib import contextmanager

# Mengambil URL dari file .streamlit/secrets.toml
DB_URL = st.secrets["DB_URL"]

@contextmanager
def get_db_connection():
    """
    Context manager untuk koneksi database.
    Otomatis membuka koneksi dan menjamin penutupan koneksi.
    """
    conn = psycopg2.connect(DB_URL)
    try:
        yield conn
    finally:
        conn.close()

@st.cache_data(ttl=600)
def jalankan_query(sql, param=(), commit=False):
    """
    Menjalankan query dengan context manager yang aman.
    """
    data = None
    try:
        # Menggunakan 'with' agar koneksi otomatis tertutup
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, param)
                if not commit:
                    data = cursor.fetchall()
                else:
                    conn.commit()
    except Exception as e:
        st.error(f"Error Database: {e}")
    
    return data

def jalankan_query_satu(sql, param=()):
    """Mengambil hanya satu baris data, lebih efisien untuk pencarian tunggal."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, param)
                return cursor.fetchone()
    except Exception as e:
        st.error(f"Error Database: {e}")
        return None

def get_stok_rendah(batas):
    # Gunakan string biasa tanpa spasi aneh
    query = "SELECT nama_barang, stok_sistem FROM barang WHERE stok_sistem <= %s"
    return jalankan_query(query, (batas,))

def get_data_barang(role):
    """
    Mengambil data barang berdasarkan peran pengguna.
    """
    # Contoh koneksi database (sesuaikan dengan kode Anda saat ini)
    # conn = connect_db() 
    
    if role == "admin":
        # Admin bisa melihat seluruh data
        query = "SELECT * FROM inventory"
    else:
        # User biasa hanya melihat barang yang statusnya 'tersedia'
        query = "SELECT * FROM inventory WHERE status = 'tersedia'"

def cek_barang_ada(nama_barang):
    # Mengecek apakah nama barang sudah ada (case-insensitive)
    query = "SELECT COUNT(*) FROM barang WHERE LOWER(nama_barang) = LOWER(%s)"
    hasil = jalankan_query(query, (nama_barang,))
    # hasil akan berupa list berisi tuple, misal: [(1,)]
    return hasil[0][0] > 0

def export_to_excel_filter(nama_barang, jenis_transaksi, tgl_awal, tgl_akhir, sub_bagian):
    # Mengambil data
    data = ambil_riwayat_terfilter(nama_barang, jenis_transaksi, tgl_awal, tgl_akhir, sub_bagian)
    
    nama_kolom = ["Kode Barang", "Nama Barang", "Jenis Transaksi", "Jumlah", "Satuan", "Tanggal", "Keterangan"]
    df = pd.DataFrame(data, columns=nama_kolom)
    
    # --- MENAMBAHKAN FORMAT TANGGAL ---
    # 1. Pastikan kolom tanggal bertipe datetime
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    # 2. Ubah format menjadi teks DD/MM/YYYY agar rapi di Excel
    df["Tanggal"] = df["Tanggal"].dt.strftime("%d/%m/%Y")
    
    # Renaming kolom
    df = df.rename(columns={
        "Kode Barang": "Kode",
        "Nama Barang": "Nama Produk",
        "Jenis Transaksi": "Kategori",
        "Keterangan": "Tujuan / Sub-Bagian"
    })
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        judul = pd.DataFrame([["Laporan Inventaris Gudang", "", "", "", "", "", ""]])
        judul.to_excel(writer, index=False, header=False, startrow=0)
        
        df.to_excel(writer, index=False, sheet_name='Laporan', startrow=2)
        
    buffer.seek(0)
    return buffer.getvalue()

def jalankan_perintah_db(sql, params=()):
    """Fungsi untuk perintah INSERT, UPDATE, atau DELETE yang butuh commit"""
    conn = psycopg2.connect(DB_URL) # Sesuaikan dengan variabel koneksi Anda
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
    finally:
        conn.close()

def update_stok_opname(data_list):
    """Logika untuk update stok dan insert log secara batch"""
    conn = psycopg2.connect(DB_URL)
    try:
        with conn:
            with conn.cursor() as cursor:
                # Update stok
                sql_update = "UPDATE barang SET stok_sistem = %s WHERE kode_barang = %s"
                psycopg2.extras.execute_batch(cursor, sql_update, [(d[0], d[2]) for d in data_list])
                
                # Insert log
                sql_log = "INSERT INTO log_opname (kode_barang, stok_sebelum, stok_sesudah) VALUES (%s, %s, %s)"
                psycopg2.extras.execute_batch(cursor, sql_log, [(d[2], d[1], d[0]) for d in data_list])
    finally:
        conn.close()

def ambil_data_log():
    """
    Mengambil data log dari tabel log_opname.
    Fungsi ini diletakkan di db_utils agar bisa digunakan di banyak halaman.
    """
    # Menggunakan fungsi jalankan_query yang sudah ada di file ini
    query = "SELECT id, kode_barang, stok_sebelum, stok_sesudah, waktu_opname, petugas FROM log_opname ORDER BY id DESC LIMIT 50"
    
    data = jalankan_query(query)
    
    # Memproses data menjadi DataFrame
    if not data:
        return pd.DataFrame(columns=["ID", "Kode Barang", "Stok Sebelum", "Stok Sesudah", "Tanggal"])
    
    df = pd.DataFrame(data, columns=["ID", "Kode Barang", "Stok Sebelum", "Stok Sesudah", "Tanggal"])
    return df

def sinkronisasi_riwayat_masuk(raw_riwayat, id_terlihat, set_id_sekarang, edited_df):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Ambil semua data barang terkait sekaligus untuk efisiensi
                cursor.execute("SELECT nama_barang, stok_sistem FROM barang FOR UPDATE")
                stok_map = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 2. Proses Penghapusan Baris
                for baris in raw_riwayat:
                    id_asal = baris[0]
                    if id_asal in id_terlihat and id_asal not in set_id_sekarang:
                        nm_b, jml_lama = baris[2], baris[3]
                        stok_map[nm_b] = max(0, stok_map[nm_b] - jml_lama)
                        cursor.execute("DELETE FROM riwayat WHERE id = %s", (id_asal,))
                
                # 3. Proses Perubahan/Edit Data
                for _, row in edited_df.iterrows():
                    id_cek = row["ID Transaksi"]
                    jml_baru = int(row["Jumlah"])
                    ket_baru = str(row["Keterangan"])
                    
                    data_lama = [b for b in raw_riwayat if b[0] == id_cek][0]
                    if jml_baru != data_lama[3] or ket_baru != data_lama[5]:
                        selisih = jml_baru - data_lama[3]
                        stok_map[data_lama[2]] += selisih
                        cursor.execute("UPDATE riwayat SET jumlah = %s, keterangan = %s WHERE id = %s", 
                                       (jml_baru, ket_baru, id_cek))
                
                # 4. Update stok ke database secara akhir (efisiensi)
                for nama_barang, stok_baru in stok_map.items():
                    cursor.execute("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", 
                                   (stok_baru, nama_barang))
                
                conn.commit()
        return True, "Perubahan riwayat masuk berhasil disinkronisasi!"
    except Exception as e:
        return False, f"Gagal menyinkronkan data: {str(e)}"

def sinkronisasi_riwayat_keluar(raw_riwayat, id_terlihat, set_id_sekarang, edited_df):
    """
    Menjalankan transaksi sinkronisasi barang keluar dengan aman.
    Termasuk validasi agar stok tidak menjadi negatif akibat pengeditan.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Proses Penghapusan Baris
                for baris in raw_riwayat:
                    id_asal = baris[0]
                    if id_asal in id_terlihat and id_asal not in set_id_sekarang:
                        nm_b, jml_lama = baris[2], baris[3]
                        
                        cursor.execute("SELECT stok_sistem FROM barang WHERE nama_barang = %s FOR UPDATE", (nm_b,))
                        stok_skrg = cursor.fetchone()[0]
                        
                        # Tambah stok kembali karena riwayat KELUAR-nya dihapus
                        cursor.execute("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_skrg + jml_lama, nm_b))
                        cursor.execute("DELETE FROM riwayat WHERE id = %s", (id_asal,))
                
                # 2. Proses Perubahan/Edit Data
                for _, row in edited_df.iterrows():
                    id_cek = row["ID Transaksi"]
                    jml_baru = int(row["Jumlah"])
                    ket_baru = str(row["Keterangan/Tujuan"])
                    
                    data_lama = [b for b in raw_riwayat if b[0] == id_cek][0]
                    jml_lama = data_lama[3]
                    nm_b = data_lama[2]
                    
                    if jml_baru != jml_lama or ket_baru != data_lama[5]:
                        selisih = jml_baru - jml_lama
                        
                        cursor.execute("SELECT stok_sistem FROM barang WHERE nama_barang = %s FOR UPDATE", (nm_b,))
                        stok_skrg = cursor.fetchone()[0]
                        
                        # VALIDASI ERROR: Cek apakah stok cukup jika jumlah keluar diperbesar
                        if stok_skrg - selisih < 0:
                            raise ValueError(f"Stok untuk '{nm_b}' tidak mencukupi jika jumlah keluar diubah menjadi {jml_baru} (Sisa stok saat ini: {stok_skrg}).")
                            
                        cursor.execute("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_skrg - selisih, nm_b))
                        cursor.execute("UPDATE riwayat SET jumlah = %s, keterangan = %s WHERE id = %s", (jml_baru, ket_baru, id_cek))
                
                # Jika semua lancar, simpan permanen
                conn.commit()
        return True, "Perubahan riwayat keluar berhasil disimpan!"
    except Exception as e:
        return False, f"Gagal menyinkronkan data: {str(e)}"

def ambil_riwayat_terfilter(nama_barang, jenis_transaksi, tgl_awal, tgl_akhir, sub_bagian=None):
    """
    Mengambil riwayat dengan filter tambahan untuk sub-bagian (keterangan).
    """
    query = "SELECT kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan FROM riwayat WHERE 1=1"
    params = []

    if nama_barang:
        query += " AND nama_barang ILIKE %s"
        params.append(f"%{nama_barang}%")
    
    if jenis_transaksi:
        format_strings = ','.join(['%s'] * len(jenis_transaksi))
        query += f" AND jenis_transaksi IN ({format_strings})"
        params.extend(jenis_transaksi)
        
    # Filter tambahan untuk sub-bagian (mencari di kolom keterangan)
    if sub_bagian:
        query += " AND keterangan ILIKE %s"
        params.append(f"%{sub_bagian}%")
        
    query += " AND tanggal::date BETWEEN %s AND %s"
    params.extend([tgl_awal, tgl_akhir])
    
    query += " ORDER BY id DESC"
    
    return jalankan_query(query, tuple(params))

def autentikasi_user(username, password):
    # Sekarang menggunakan jalankan_query_satu
    hasil = jalankan_query_satu("SELECT password_hash, role FROM users WHERE username = %s", (username,))
    if hasil:
        if bcrypt.checkpw(password.encode('utf-8'), hasil[0].encode('utf-8')):
            return hasil[1]
    return None
