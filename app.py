import streamlit as st 
import numpy as np
import pandas as pd
from datetime import datetime

# --- App Configuration ---
st.set_page_config(page_title="AI Sports Betting Value Tool", layout="wide")

# --- Title Section ---
st.title("🤖 AI Sports Betting Value Estimator")
st.caption("Smart value bet identification using probability models and bankroll optimization.")

# --- Sidebar Settings ---
with st.sidebar:
    st.header("⚙️ Settings")
    bankroll = st.number_input("💰 Your Bankroll ($)", min_value=0.0, value=1000.0, step=100.0)
    use_kelly = st.checkbox("📐 Use Kelly Criterion", value=True)
    kelly_fraction = st.slider("Kelly Fraction", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
    st.markdown("---")
    st.info("Adjust settings to tailor bet sizing to your risk tolerance.")

# --- Main Columns ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Bet Details")
    odds_format = st.radio("Select Odds Format:", ["American", "Decimal"], horizontal=True)

    if odds_format == "American":
        book_odds = st.number_input("Bookmaker Odds (e.g. +150 or -110)", value=150)
        if book_odds > 0:
            decimal_odds = (book_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(book_odds)) + 1
    else:
        decimal_odds = st.number_input("Decimal Odds", value=2.50, min_value=1.01, step=0.01)

    win_probability = st.slider("Estimated Win Probability (%)", min_value=1, max_value=99, value=50)
    event_name = st.text_input("Event Name")
    stake = st.number_input("Stake Amount ($)", min_value=0.0, value=100.0, step=10.0)

with col2:
    st.subheader("📈 Bet Analysis")
    try:
        ev = (decimal_odds * (win_probability / 100)) - 1
        ev_percent = ev * 100
        implied_prob = (1 / decimal_odds) * 100
        edge = win_probability - implied_prob

        if ev > 0:
            st.success(f"✅ +EV Bet Detected! Expected Return: {ev_percent:.2f}%")
        else:
            st.error(f"❌ -EV Bet: Expected Return: {ev_percent:.2f}%")

        st.metric("Your Probability", f"{win_probability:.1f}%")
        st.metric("Implied Probability", f"{implied_prob:.1f}%")
        st.metric("Edge", f"{edge:.1f}%")

        if use_kelly:
            kelly_bet = ((win_probability/100 * decimal_odds) - 1) / (decimal_odds - 1)
            kelly_bet = max(0, kelly_bet)
            recommended_bet = kelly_bet * kelly_fraction * bankroll

            st.subheader("🧠 Kelly Recommendation")
            st.metric("Kelly %", f"{kelly_bet*100:.2f}%")
            st.metric("Adjusted Kelly", f"{kelly_bet*kelly_fraction*100:.2f}%")
            st.metric("Recommended Bet", f"${recommended_bet:.2f}")
            potential_profit = recommended_bet * (decimal_odds - 1)
            st.metric("Potential Profit", f"${potential_profit:.2f}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- Tabs for More Features ---
tab1, tab2 = st.tabs(["📚 Bet History", "🎓 Learning Center"])

with tab1:
    st.subheader("📅 Bet History Log")
    if st.button("💾 Save This Bet"):
        try:
            try:
                bets_df = pd.read_csv("bet_history.csv")
            except:
                bets_df = pd.DataFrame(columns=["Date", "Event", "Odds", "Probability", "EV%", "Stake"])

            new_bet = pd.DataFrame({
                "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                "Event": [event_name if event_name else "Unnamed Event"],
                "Odds": [decimal_odds],
                "Probability": [win_probability],
                "EV%": [ev_percent],
                "Stake": [stake]
            })

            bets_df = pd.concat([bets_df, new_bet], ignore_index=True)
            bets_df.to_csv("bet_history.csv", index=False)
            st.success("✅ Bet saved successfully!")
        except Exception as e:
            st.error(f"❌ Could not save bet: {e}")

    try:
        bets_df = pd.read_csv("bet_history.csv")
        if not bets_df.empty:
            st.dataframe(bets_df)
        else:
            st.info("No bets recorded yet.")
    except:
        st.info("No bet history file found.")

with tab2:
    st.subheader("📖 Betting Education")
    st.markdown("""
    ### 🔍 Expected Value (EV)
    EV = (Decimal Odds × Win Probability) - 1

    A positive EV indicates long-term profitability.

    ### 🧠 Kelly Criterion
    Formula: (p × b - q) / b  
    Where:
    - p = Probability of winning
    - q = Probability of losing = (1 - p)
    - b = Odds - 1

    ### 🧾 Edge = Your Probability - Implied Probability
    Implied = 1 / Decimal Odds
    """)

# --- Footer ---
st.markdown("---")
st.caption("This AI-driven tool is for educational and entertainment purposes only. Always gamble responsibly.")
