import pandas as pd
import io
import psycopg2
import psycopg2.extras
import streamlit as st
import bcrypt

# Gunakan secrets untuk keamanan (opsional tapi sangat disarankan)
# Jika tidak ingin pakai secrets, masukkan URL di sini
DB_URL = "postgresql://postgres.krckbruwpxgiziujgqiy:1P%40ny001%2E%2E%2E@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

def get_connection():
    return psycopg2.connect(DB_URL)

def jalankan_query(sql, param=(), commit=False):
    conn = get_connection()
    cursor = conn.cursor()
    data = None
    try:
        cursor.execute(sql, param)
        if not commit:
            data = cursor.fetchall()
        else:
            conn.commit()
    except Exception as e:
        st.error(f"Error Database: {e}")
    finally:
        cursor.close()
        conn.close()
    return data

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

def export_to_excel(query, params=(), kolom_pilihan=None):
    # 1. Jalankan query
    data = jalankan_query(query, params)
    
    # Debug: Pastikan data tidak kosong
    if not data:
        st.error("Data dari database kosong, tidak bisa membuat file Excel.")
        return None

    df = pd.DataFrame(data)
    st.write("Kolom yang tersedia di database:", df.columns.tolist())
    
    # 2. Filter kolom (opsional)
    if kolom_pilihan:
        kolom_yang_ada = [k for k in kolom_pilihan if k in df.columns]
        if kolom_yang_ada:
            df = df[kolom_yang_ada]
        else:
            st.warning("Kolom pilihan tidak ditemukan, mengekspor semua kolom.")
    
    # 3. Simpan ke buffer dengan penanganan error
    buffer = io.BytesIO()
    try:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        
        # Pindahkan kursor ke awal agar bisa dibaca oleh st.download_button
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Gagal menulis ke Excel: {e}")
        return None
