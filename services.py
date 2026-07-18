import streamlit as st
from db_utils import get_db_connection

def sinkronisasi_riwayat_masuk(raw_riwayat, id_terlihat, set_id_sekarang, edited_df):
    """Menangani sinkronisasi barang masuk dengan logika dictionary mapping."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nama_barang, stok_sistem FROM barang FOR UPDATE")
                stok_map = {row[0]: row[1] for row in cursor.fetchall()}
                
                for baris in raw_riwayat:
                    id_asal = baris[0]
                    if id_asal in id_terlihat and id_asal not in set_id_sekarang:
                        nm_b, jml_lama = baris[2], baris[3]
                        stok_map[nm_b] = max(0, stok_map[nm_b] - jml_lama)
                        cursor.execute("DELETE FROM riwayat WHERE id = %s", (id_asal,))
                
                for _, row in edited_df.iterrows():
                    id_cek = row["ID Transaksi"]
                    jml_baru = int(row["Jumlah"])
                    ket_baru = str(row["Keterangan"])
                    
                    data_lama = [b for b in raw_riwayat if b[0] == id_cek][0]
                    if jml_baru != data_lama[3] or ket_baru != data_lama[5]:
                        selisih = jml_baru - data_lama[3]
                        stok_map[data_lama[2]] += selisih
                        cursor.execute("UPDATE riwayat SET jumlah = %s, keterangan = %s WHERE id = %s", (jml_baru, ket_baru, id_cek))
                
                for nama_barang, stok_baru in stok_map.items():
                    cursor.execute("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang))
                
                conn.commit()
        return True, "Perubahan riwayat masuk berhasil disinkronisasi!"
    except Exception as e:
        return False, f"Gagal menyinkronkan data: {str(e)}"

def sinkronisasi_riwayat_keluar(raw_riwayat, id_terlihat, set_id_sekarang, edited_df):
    """Menangani sinkronisasi barang keluar dengan logika dictionary mapping."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT nama_barang, stok_sistem FROM barang FOR UPDATE")
                stok_map = {row[0]: row[1] for row in cursor.fetchall()}
                
                for baris in raw_riwayat:
                    id_asal = baris[0]
                    if id_asal in id_terlihat and id_asal not in set_id_sekarang:
                        nm_b, jml_lama = baris[2], baris[3]
                        stok_map[nm_b] += jml_lama
                        cursor.execute("DELETE FROM riwayat WHERE id = %s", (id_asal,))
                
                for _, row in edited_df.iterrows():
                    id_cek = row["ID Transaksi"]
                    jml_baru = int(row["Jumlah"])
                    ket_baru = str(row["Keterangan/Tujuan"])
                    
                    data_lama = [b for b in raw_riwayat if b[0] == id_cek][0]
                    jml_lama = data_lama[3]
                    nm_b = data_lama[2]
                    
                    if jml_baru != jml_lama or ket_baru != data_lama[5]:
                        selisih = jml_baru - jml_lama
                        if stok_map[nm_b] - selisih < 0:
                            raise ValueError(f"Stok untuk '{nm_b}' tidak mencukupi.")
                        stok_map[nm_b] -= selisih
                        cursor.execute("UPDATE riwayat SET jumlah = %s, keterangan = %s WHERE id = %s", (jml_baru, ket_baru, id_cek))
                
                for nama_barang, stok_baru in stok_map.items():
                    cursor.execute("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang))
                
                conn.commit()
        return True, "Perubahan riwayat keluar berhasil disimpan!"
    except Exception as e:
        return False, f"Gagal menyinkronkan data: {str(e)}"
