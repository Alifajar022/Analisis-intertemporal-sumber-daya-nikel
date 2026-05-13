import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Header
st.set_page_config(page_title="Simulasi nikel PT StanIndo", layout="wide")
st.title("Alat Simulasi Harga & Alokasi Sumber Daya Nikel")
st.markdown("Studi Kasus: PT StanIndo Inti Perkasa")

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
        fill='tozeroy'
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

st.table(df.head(11))
st.write
