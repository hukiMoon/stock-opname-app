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

def get_stok_rendah(batas=5):
    # Mengambil barang yang stoknya kurang dari atau sama dengan batas
    query = "SELECT nama_barang, stok_sistem FROM barang WHERE stok_sistem <= %s"
    return jalankan_query(query, (batas,))

def register_user(username, password, role):
    # Hash password sebelum disimpan
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    query = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
    # jalankan_query(query, (username, hashed.decode('utf-8'), role))
