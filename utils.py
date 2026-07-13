import streamlit as st

def init_login_state():
    """Memastikan variabel sesi login selalu terinisialisasi."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

def check_login():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Anda harus login terlebih dahulu.")
        st.stop()

def logout():
    """Fungsi untuk membersihkan sesi login."""
    st.session_state["logged_in"] = False
    st.rerun()

def tampilkan_sidebar():
    st.sidebar.title("Navigasi Menu")
    st.sidebar.success("Anda berhasil login!")
    
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun() # Refresh halaman untuk kembali ke layar login

# 1. Fungsi untuk membuat tampilan kartu (card) yang Anda butuhkan
def card_container(title):
    st.subheader(title)
    return st.container(border=True)

# 2. Fungsi untuk gaya/styling (misalnya pesan sukses/error yang seragam)
def tampilkan_pesan_sukses(pesan):
    st.success(f"✅ {pesan}")

# 3. Fungsi format angka (agar tampilan mata uang lebih rapi)
def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

# 4. Fungsi bantu lainnya (misalnya untuk reset state)
def reset_input():
    st.session_state["input_reset"] = True
