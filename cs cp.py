import streamlit as st
import math
import matplotlib.pyplot as plt # Tambah library ini

# --- FUNGSI SEDIA ADA (TIDAK DIUBAH) ---
def dms_to_dd(d, m, s):
    return d + (m / 60.0) + (s / 3600.0)

def check_class(accuracy):
    if accuracy >= 8000: return "Kelas 1 (Lulus)", "green"
    elif accuracy >= 4000: return "Kelas 2 (Lulus)", "blue"
    else: return "Kelas 3 (Lulus/Gagal mengikut had)", "orange"

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Kira Traverse Digital", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- MUKA DEPAN ---
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/0/03/Logo_Politeknik_Malaysia.png", width=250)
    
    st.markdown("<h1 style='text-align: center;'>SISTEM KIRA TRAVERSE DIGITAL</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>📍 Politeknik Ungku Omar</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    ---
    <div style="text-align: center;">
        <strong>DISEDIAKAN OLEH:</strong><br>
        1. NUR FADILAH ADHA BINTI MOHD FAUZI<br>
        2. SITI ZULAIKA BINTI AHMAD NIZAM<br>
        3. NUR AQILAH BINTI YUSZAILEE
    </div>
    ---
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        st.write("### Sila Log Masuk")
        user_id = st.text_input("ID Pengguna (Bebas)")
        password = st.text_input("Kata Laluan", type="password")
        
        if st.button("Log Masuk", use_container_width=True):
            if password == "admin123":
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user_id
                st.rerun()
            else:
                st.error("Kata laluan salah!")

# --- KANDUNGAN UTAMA ---
else:
    with st.sidebar:
        st.write(f"👤 Pengguna: **{st.session_state['user_id']}**")
        if st.button("Log Keluar"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.divider()
        st.header("Konfigurasi")
        n_lines = st.number_input("Bilangan Garisan", min_value=1, max_value=50, value=8)

    st.title("🏗️ Sistem Kiraan Trabas (Linear Misclosure)")

    total_north = 0.0
    total_south = 0.0
    total_east = 0.0
    total_west = 0.0
    total_dist = 0.0
    
    # List untuk menyimpan koordinat plot
    coords_x = [0.0]
    coords_y = [0.0]
    current_x = 0.0
    current_y = 0.0

    st.subheader("Input Jarak dan Bering (DMS)")
    cols = st.columns(2)

    for i in range(n_lines):
        stn_label = i + 2 if i < n_lines - 1 else 1
        with cols[i % 2]:
            with st.expander(f"📍 Stesen {stn_label}", expanded=True):
                dist = st.number_input(f"Jarak (m)", key=f"d{i}", format="%.3f")
                c1, c2, c3 = st.columns(3)
                d = c1.number_input(f"D (°)", key=f"deg{i}", step=1)
                m = c2.number_input(f"M (')", key=f"min{i}", step=1)
                s = c3.number_input(f"S ('')", key=f"sec{i}", step=1)
                
                dd = dms_to_dd(d, m, s)
                bearing_rad = math.radians(dd)
                
                latit = round(dist * math.cos(bearing_rad), 3)
                ditit = round(dist * math.sin(bearing_rad), 3)
                
                # Update koordinat untuk polygon
                current_y += latit
                current_x += ditit
                coords_x.append(current_x)
                coords_y.append(current_y)
                
                if latit >= 0: total_north += latit
                else: total_south += abs(latit)
                
                if ditit >= 0: total_east += ditit
                else: total_west += abs(ditit)
                
                total_dist += dist

    st.divider()

    if total_dist > 0:
        delta_l = round(total_north - total_south, 3)
        delta_d = round(total_east - total_west, 3)
        misclosure = math.sqrt(pow(delta_l, 2) + pow(delta_d, 2))
        accuracy_ratio = total_dist / misclosure if misclosure > 0 else 999999
        status, warna = check_class(accuracy_ratio)

        res_c1, res_c2 = st.columns(2)
        with res_c1:
            st.write("### Analisis Latit (+L / -L)")
            st.write(f"Jumlah Utara (+L): `{total_north:.3f}`")
            st.write(f"Jumlah Selatan (-L): `{total_south:.3f}`")
            st.info(f"**Beza Latit (ΔL):** `{delta_l:.3f}`")

        with res_c2:
            st.write("### Analisis Dipat (+D / -D)")
            st.write(f"Jumlah Timur (+D): `{total_east:.3f}`")
            st.write(f"Jumlah Barat (-D): `{total_west:.3f}`")
            st.info(f"**Beza Dipat (ΔD):** `{delta_d:.3f}`")

        st.subheader("Hasil Akhir")
        st.success(f"**Linear Misclosure:** `{misclosure:.4f} m` (√{delta_l}² + {delta_d}²)")
        st.metric("Nisbah Ketepatan", f"1 : {int(accuracy_ratio)}")
        st.markdown(f"Status Pengelasan: **:{warna}[{status}]**")
        
        # --- BAHAGIAN LUKISAN POLYGON ---
        st.divider()
        st.subheader("📊 Plot Poligon Trabas")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(coords_x, coords_y, marker='o', color='red', linestyle='-')
        
        # Labelkan setiap stesen
        for idx, (x, y) in enumerate(zip(coords_x, coords_y)):
            label = idx + 1 if idx < n_lines else 1
            ax.text(x, y, f"  Stn {label}", fontsize=9)
            
        ax.set_xlabel("Timur / Barat (Ditit)")
        ax.set_ylabel("Utara / Selatan (Latit)")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_aspect('equal', adjustable='box') # Penting supaya skala X dan Y sama
        
        st.pyplot(fig)
        
    else:
        st.warning("Sila masukkan data jarak untuk mulakan kiraan.")