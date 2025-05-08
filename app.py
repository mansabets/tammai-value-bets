# NEURAL EDGE BETTING INTELLIGENCE PLATFORM
# Advanced AI Sports Betting Value Tool

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
import time
from datetime import datetime

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(
    page_title="NeuralEdge Betting Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🧠"
)

# Custom CSS injection
st.markdown("""
<style>
:root {
    --primary: #6e00ff;
    --secondary: #00d4ff;
    --dark: #0e1117;
    --light: #f8f9fa;
    --success: #00ff88;
    --danger: #ff3860;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}

[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.8) !important;
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

.custom-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.glass-button {
    background: rgba(110, 0, 255, 0.2) !important;
    border: 1px solid var(--primary) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
}

.glass-button:hover {
    background: rgba(110, 0, 255, 0.4) !important;
    transform: translateY(-2px);
}

.pulse-animation {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0, 212, 255, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(0, 212, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 212, 255, 0); }
}
</style>
""", unsafe_allow_html=True)

# ======================
# CORE FUNCTIONS
# ======================
def create_probability_radar_chart(your_prob, implied_prob):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[your_prob, implied_prob, abs(your_prob - implied_prob)*3, your_prob],
        theta=['Your Model', 'Market Implied', 'Edge', 'Your Model'],
        fill='toself',
        name='Your Assessment',
        line_color='#00ff88'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=0, l=0, r=0),
        height=250
    )
    return fig

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown("""
    <div style='border-left: 3px solid var(--secondary); padding-left: 15px; margin-bottom: 30px;'>
    <h2 style='color: white; margin-bottom: 0;'>SYSTEM CONTROLS</h2>
    <p style='color: rgba(255,255,255,0.6); font-size: 0.8rem;'>NEURAL EDGE v2.1.4</p>
    </div>
    """, unsafe_allow_html=True)
   
    bankroll = st.number_input("💰 BANKROLL CAPITAL", min_value=0.0, value=10000.0, step=100.0)
    use_kelly = st.toggle("ACTIVATE KELLY CRITERION", value=True)
    kelly_fraction = st.slider("RISK APPETITE", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

# ======================
# MAIN INTERFACE
# ======================
# Header
st.markdown("""
<h1 style='color: white; font-size: 2.5rem; margin-bottom: 0;'>
<span style='color: var(--secondary);'>NEURAL</span>EDGE BETTING INTELLIGENCE
</h1>
<p style='color: rgba(255,255,255,0.7); font-size: 1.1rem;'>
Quantum-powered value detection • Deep learning probability models
</p>
""", unsafe_allow_html=True)

# Main columns
col1, col2 = st.columns([1,1], gap="large")

with col1:
    with st.container():
        st.markdown("<div class='custom-card pulse-animation'>", unsafe_allow_html=True)
        st.subheader("🧠 AI BET INPUT CONSOLE")
       
        odds_format = st.radio("ODDS FORMAT:", ["American", "Decimal"], horizontal=True)
       
        if odds_format == "American":
            book_odds = st.number_input("BOOKMAKER ODDS", value=150)
            decimal_odds = (book_odds / 100) + 1 if book_odds > 0 else (100 / abs(book_odds)) + 1
        else:
            decimal_odds = st.number_input("DECIMAL ODDS", value=2.50, min_value=1.01, step=0.01)
       
        win_probability = st.slider("AI-ESTIMATED WIN PROBABILITY (%)", min_value=1, max_value=99, value=50)
        event_name = st.text_input("EVENT IDENTIFIER")
        stake = st.number_input("STAKE AMOUNT ($)", min_value=0.0, value=100.0, step=10.0)
       
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("📊 QUANTUM ANALYSIS OUTPUT")
       
        try:
            ev = (decimal_odds * (win_probability / 100)) - 1
            ev_percent = ev * 100
            implied_prob = (1 / decimal_odds) * 100
           
            if ev > 0:
                st.success(f"""
                🚀 **POSITIVE EV DETECTED**  
                **Expected Return:** {ev_percent:.2f}%  
                **Confidence Level:** {win_probability:.1f}%
                """)
            else:
                st.error(f"""
                ⚠️ **NEGATIVE EV WARNING**  
                **Expected Loss:** {abs(ev_percent):.2f}%
                """)
           
            cols = st.columns(3)
            with cols[0]:
                st.metric("YOUR PROB", f"{win_probability:.1f}%", delta="AI Model")
            with cols[1]:
                st.metric("IMPLIED PROB", f"{implied_prob:.1f}%", delta="Market")
            with cols[2]:
                st.metric("EDGE", f"{(win_probability - implied_prob):.1f}%", delta_color="inverse")
           
            st.plotly_chart(create_probability_radar_chart(win_probability, implied_prob), use_container_width=True)
           
        except Exception as e:
            st.error(f"SYSTEM ERROR: {str(e)}")
       
        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.5); font-size: 0.8rem;'>
<p>NEURAL EDGE BETTING INTELLIGENCE PLATFORM</p>
</div>
""", unsafe_allow_html=True)
