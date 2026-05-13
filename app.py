import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Header
st.set_page_config(page_title="Simulasi nikel PT StanIndo", layout="wide")
st.title("🚀 Alat Simulasi Harga & Alokasi Sumber Daya Nikel")
st.markdown("### Studi Kasus: PT StanIndo Inti Perkasa")

# --- PARAMETER BERDASARKAN DOKUMEN PERUSAHAAN ---
# Fungsi Permintaan: P = 31.000 - 11q
a_default = 31000 
b_default = 11    
mc_default = 6000 # Rata-rata Marginal Cost riil
s_default = 20000 # Total Cadangan (S)
r_default = 0.05  # Tingkat diskonto (5%)

# Sidebar Input
st.sidebar.header("Konfigurasi Parameter")
market_type = st.sidebar.selectbox("Mekanisme Pasar", ["Persaingan Sempurna", "Monopoli", "Oligopoli"])
r = st.sidebar.slider("Tingkat Diskonto (r)", 0.01, 0.20, r_default)
S_total = st.sidebar.number_input("Total Cadangan (Ton)", value=s_default)
mc = st.sidebar.number_input("Marginal Cost (US$/Ton)", value=mc_default)

# --- ENGINE SIMULASI ---
def run_simulation():
    t_max = 30
    # MUC awal berdasarkan dokumen adalah 15.163
    muc0 = 15163 
    
    results = []
    current_S = S_total
    
    for t in range(t_max):
        # Hotelling Rule: MUC_t = MUC_0 * e^(rt)
        muc_t = muc0 * np.exp(r * t)
        
        if market_type == "Persaingan Sempurna":
            p_t = mc + muc_t
        elif market_type == "Monopoli":
            # MR = MC + MUC -> (a - 2bq) = MC + MUC
            p_t = (a_default + mc + muc_t) / 2
        else: # Oligopoli (Asumsi Cournot dengan 3 pemain)
            p_t = (a_default + 3 * (mc + muc_t)) / 4
            
        # Laju Ekstraksi q = (a - P) / b
        q_t = max(0, (a_default - p_t) / b_default)
        
        if current_S <= 0:
            q_t = 0
            p_t = a_default
        elif current_S < q_t:
            q_t = current_S
            current_S = 0
        else:
            current_S -= q_t
            
        results.append({
            "Tahun": t, 
            "Harga (P)": round(p_t, 2), 
            "MUC": round(muc_t, 2),
            "Ekstraksi (q)": round(q_t, 2), 
            "Sisa Stok": round(current_S, 2)
        })
        
    return pd.DataFrame(results)

df = run_simulation()

# --- DISPLAY UI ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Tren Harga & MUC")
    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(x=df['Tahun'], y=df['Harga (P)'], name="Harga Jual"))
    fig_p.add_trace(go.Scatter(x=df['Tahun'], y=df['MUC'], name="Marginal User Cost", line=dict(dash='dash')))
    st.plotly_chart(fig_p, use_container_width=True)

with col2:
    st.subheader("Laju Ekstraksi vs Sisa Stok")
    fig_q = go.Figure()
    fig_q.add_trace(go.Scatter(x=df['Tahun'], y=df['Ekstraksi (q)'], name="Produksi (q)", fill='tozeroy'))
    fig_q.add_trace(go.Scatter(x=df['Tahun'], y=df['Sisa Stok'], name="Cadangan Tersisa"))
    st.plotly_chart(fig_q, use_container_width=True)
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
st.table(df.head(11))
