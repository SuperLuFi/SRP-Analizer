import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import savgol_filter

# --- Sidebar ---
st.sidebar.title("⚙️ Pengaturan Analisis")
uploaded_file = st.sidebar.file_uploader("Upload CSV Surface Card", type="csv")

# Parameter
window = st.sidebar.slider("Smoothing Window", 3, 51, 11, step=2)
poly = st.sidebar.slider("Polynomial Order", 1, 5, 2)
spm = st.sidebar.number_input("Stroke Per Minute (SPM)", 1, 60, 15)

# Tombol reset
if st.sidebar.button("🔄 Reset"):
    window, poly, spm = 11, 2, 15
    st.rerun()

st.title("📊 Sucker Rod Pump Analyzer Dashboard")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- Surface Data ---
    Xs, Fs = df['Displacement'], df['Rod Load']

    # --- Downhole (smoothing) ---
    Fd = savgol_filter(Fs, window, poly)

    # --- Plot ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Xs, y=Fs, mode='lines', name='Surface Card', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=Xs, y=Fd, mode='lines', name='Downhole Card (Reconstructed)', line=dict(color='green')))
    fig.update_layout(title="Surface vs Downhole Dynamometer Card",
                      xaxis_title="Displacement (in)",
                      yaxis_title="Load (lbf)",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # --- Volume Estimation ---
    stroke_vol = np.trapezoid(Fd, Xs)
    vol_per_min = stroke_vol * spm
    total_vol = vol_per_min * 60  # asumsi per jam

    st.subheader("📈 Hasil Analisis")
    col1, col2, col3 = st.columns(3)
    col1.metric("Stroke Volume", f"{stroke_vol:,.2f} bbl")
    col2.metric("Rate", f"{vol_per_min:,.0f} bbl/min")
    col3.metric("Est. Hourly Volume", f"{total_vol:,.0f} bbl/hr")

    # --- Diagnosis ---
    diff = np.abs(Fs - Fd).mean()
    if diff < 100:
        status = "✅ Normal Pumping"
    elif diff < 500:
        status = "⚠️ Fluid Pound Detected"
    else:
        status = "❌ Gas Interference / Leakage"

    st.markdown(f"### 🩺 Diagnosis: {status}")

else:
    st.info("⬅️ Upload CSV dulu untuk mulai analisis.")
