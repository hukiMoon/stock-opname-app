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

def check_role(allowed_roles):
    """
    Fungsi untuk memeriksa apakah user saat ini memiliki akses.
    allowed_roles: list atau string, misal: ["admin", "editor"]
    """
    # Ambil role dari session_state
    current_role = st.session_state.get("role", None)

    # Jika role tidak ada atau tidak termasuk dalam list yang diizinkan
    if current_role not in allowed_roles:
        st.error("🚫 Anda tidak memiliki akses ke halaman ini.")
        st.stop()
