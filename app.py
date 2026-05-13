import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 1. Judul dan Parameter (Data dari PT StanIndo Inti Perkasa)
st.title("Simulator Harga Nikel: Analisis Intertemporal")
st.sidebar.header("Input Parameter")

a = 31000  # Konstanta permintaan [cite: 12, 43]
b = 11     # Koefisien permintaan [cite: 37]
mc = st.sidebar.number_input("Marginal Cost (MC)", value=6000) # 
r = st.sidebar.slider("Tingkat Diskonto (r)", 0.01, 0.20, 0.05) # [cite: 33, 46]
S_total = st.sidebar.number_input("Total Cadangan (Ton)", value=20000) # 
market_type = st.sidebar.selectbox("Mekanisme Pasar", ["Persaingan Sempurna", "Monopoli", "Oligopoli"])

# 2. Mesin Simulasi (Engine)
def run_simulation(market, S, r, a, b, mc):
    t_max = 25
    muc0 = 15163  # MUC awal estimasi [cite: 35, 41]
    
    data = []
    current_S = S
    
    for t in range(t_max):
        # Hotelling Rule: MUC tumbuh secara eksponensial (e^rt) [cite: 93, 95]
        muc_t = muc0 * np.exp(r * t)
        
        if market == "Persaingan Sempurna":
            p_t = mc + muc_t
        elif market == "Monopoli":
            # Monopoli: MR = MC + MUC, sehingga P lebih tinggi
            p_t = (a + mc + muc_t) / 2
        else: # Oligopoli (Asumsi 3 pemain utama)
            p_t = (a + 3*(mc + muc_t)) / 4
            
        # Laju Ekstraksi berdasarkan fungsi permintaan P = a - bq -> q = (a - P)/b 
        q_t = max(0, (a - p_t) / b)
        
        if current_S < q_t:
            q_t = current_S
            current_S = 0
        else:
            current_S -= q_t
            
        data.append({"Tahun": t, "Harga": p_t, "Ekstraksi": q_t, "Sisa Stok": current_S})
        if current_S <= 0: break
            
    return pd.DataFrame(data)

# 3. Eksekusi dan Visualisasi
df_result = run_simulation(market_type, S_total, r, a, b, mc)

# Chart Harga
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=df_result['Tahun'], y=df_result['Harga'], name="Harga (P)"))
st.plotly_chart(fig_price)

# Chart Ekstraksi & Sisa Stok
st.subheader("Dinamika Ekstraksi")
st.line_chart(df_result.set_index('Tahun')[['Ekstraksi', 'Sisa Stok']])

st.write(f"**Analisis:** Pada pasar {market_type}, cadangan diperkirakan habis pada tahun ke-{df_result['Tahun'].iloc[-1]}.")

