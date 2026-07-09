import streamlit as st
import init_path # Pastikan ini ada
from auth import check_role, tampilkan_sidebar

# Pastikan user sudah login
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("auth.py") # Arahkan ke halaman login jika belum login

# Jika sudah login, tampilkan sidebar
tampilkan_sidebar()

st.title("📜 Log Aktivitas Gudang")
st.write("Selamat datang, Anda telah login!")

# 2. Mengambil data untuk statistik (opsional, tapi memperbagus tampilan)
data_riwayat = jalankan_query("SELECT kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan FROM riwayat ORDER BY id DESC")

if not data_riwayat:
    st.info("Belum ada riwayat transaksi.")
else:
    df = pd.DataFrame(data_riwayat, columns=["Kode Barang", "Nama Barang", "Jenis Transaksi", "Jumlah", "Satuan", "Tanggal Transaksi", "Keterangan"])
    
    # Menambahkan ringkasan ringkas di atas tabel
    col1, col2 = st.columns(2)
    col1.metric("Total Transaksi", len(df))
    col2.metric("Barang Terakhir Keluar", df[df["Jenis Transaksi"] == "KELUAR"].shape[0])

    # 3. Tampilan Data Modern
    st.subheader("📋 Detail Log")
    st.dataframe(
        df, 
        hide_index=True, 
        use_container_width=True,
        column_config={
            "Jenis Transaksi": st.column_config.TextColumn(
                "Jenis", 
                help="Masuk atau Keluar"
            ),
            "Tanggal Transaksi": st.column_config.DateColumn(
                "Tanggal",
                format="DD/MM/YYYY"
            )
        }
    )
