import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Konfigurasi Halaman & Judul (Sesuai Gambar)
st.set_page_config(page_title="Analisis Efisiensi Dinamis Nikel", layout="wide")

st.title("📊 Analisis Intertemporal dan Dinamika Alokasi Sumber Daya Depletable")
st.markdown("### Studi Kasus: Efisiensi Dinamis Nikel PT StanIndo Inti Perkasa")
st.write("---")

# 2. Sidebar untuk Parameter (Berdasarkan Dokumen)
st.sidebar.header("Konfigurasi Parameter")
r = st.sidebar.slider("Tingkat Diskonto (r)", 0.01, 0.20, 0.05) # Default 5% [cite: 1]
S_total = st.sidebar.number_input("Total Cadangan (Ton)", value=20000) # [cite: 1]
mc = st.sidebar.number_input("Marginal Cost (US$/Ton)", value=6000) # [cite: 1]

# Parameter Fungsi Permintaan P = 31000 - 11q [cite: 1]
a = 31000
b = 11
muc0 = 15163 # MUC awal dari hasil Goal Seek [cite: 1]

# 3. Logika Perhitungan (Hotelling Rule & Efisiensi Dinamis)
t_range = np.arange(0, 16) # Simulasi hingga 15 tahun
data = []
current_S = S_total

for t in t_range:
    # MUC_t = MUC_0 * e^(rt) 
    muc_t = muc0 * np.exp(r * t)
    p_t = mc + muc_t
    q_t = max(0, (a - p_t) / b)
    
    if current_S <= 0:
        q_t, p_t, current_S = 0, a, 0
    elif current_S < q_t:
        q_t = current_S
        current_S = 0
    else:
        current_S -= q_t
        
    data.append([t, p_t, muc_t, q_t, current_S])

df = pd.DataFrame(data, columns=['Tahun', 'Harga', 'MUC', 'Ekstraksi', 'Sisa Stok'])

# 4. Layout Visualisasi (Dua Kolom Seperti di Gambar)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Tren Harga & Marginal User Cost (MUC)")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Tahun'], y=df['Harga'], name="Harga (P)", line=dict(color='blue')))
    fig1.add_trace(go.Scatter(x=df['Tahun'], y=df['MUC'], name="MUC", line=dict(color='red', dash='dash')))
    fig1.update_layout(xaxis_title="Waktu (Tahun)", yaxis_title="US$ / Ton")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Laju Ekstraksi vs Sisa Stok")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Tahun'], y=df['Ekstraksi'], name="Ekstraksi (q)", fill='tozeroy', line=dict(color='green')))
    fig2.add_trace(go.Scatter(x=df['Tahun'], y=df['Sisa Stok'], name="Sisa Cadangan (S)", line=dict(color='orange')))
    fig2.update_layout(xaxis_title="Waktu (Tahun)", yaxis_title="Volume (Ton)")
    st.plotly_chart(fig2, use_container_width=True)

# 5. Tabel Data & Analisis (Sesuai Tahap 3 Laporan) [cite: 1]
st.write("---")
st.subheader("Tabel Proyeksi Alokasi Optimal")
st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

# 6. Refleksi Ekonomi (Berdasarkan Laporan) [cite: 1]
with st.expander("Lihat Refleksi & Makna Ekonomi"):
    st.markdown(f"""
    * **Waktu Optimal Habis Cadangan ($T^*$):** Berdasarkan simulasi, cadangan akan habis dalam **10 tahun**[cite: 1].
    * **Aset Spesial:** Penggunaan variabel *e* menunjukkan nikel sebagai aset lingkungan yang nilainya tumbuh seiring kelangkaan[cite: 1].
    * **Dampak Moral:** Jika tingkat diskonto ($r$) naik menjadi 15%, ekstraksi akan dipercepat, mengorbankan keadilan antargenerasi[cite: 1].
    """)

