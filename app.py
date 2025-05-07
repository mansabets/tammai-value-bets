import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

# App configuration
st.set_page_config(page_title="AI Sports Betting Value Tool", layout="wide")

# Main content
st.title("📊 AI Sports Betting Value Tool")
st.write("Estimate whether a bet has positive expected value (EV) and calculate optimal bet sizing.")

# Sidebar for settings
with st.sidebar:
    st.title("Settings")
    
    # Bankroll management
    bankroll = st.number_input("Your Bankroll ($)", min_value=0.0, value=1000.0, step=100.0)
    
    # Kelly Criterion settings
    use_kelly = st.checkbox("Use Kelly Criterion", value=True)
    kelly_fraction = st.slider("Kelly Fraction", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

# Main interface - two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Enter Bet Details")
    
    # Odds format selection
    odds_format = st.radio("Odds Format:", ["American", "Decimal"], horizontal=True)
    
    # Input fields based on odds format
    if odds_format == "American":
        book_odds = st.number_input("Bookmaker Odds (e.g. +150 or -110)", value=150)
        # Convert to decimal
        if book_odds > 0:
            decimal_odds = (book_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(book_odds)) + 1
    else:  # Decimal
        decimal_odds = st.number_input("Decimal Odds (e.g. 2.50)", value=2.50, min_value=1.01, step=0.01)
    
    # Win probability
    win_probability = st.slider("Estimated Win Probability (%)", min_value=1, max_value=99, value=50)
    
    # Optional bet details
    st.subheader("Optional Details")
    event_name = st.text_input("Event Name", "")
    stake = st.number_input("Stake Amount ($)", min_value=0.0, value=100.0, step=10.0)

with col2:
    st.subheader("EV Analysis")
    
    # Calculate EV
    try:
        # Calculate EV
        ev = (decimal_odds * (win_probability / 100)) - 1
        ev_percent = ev * 100
        
        # Calculate implied probability
        implied_prob = (1 / decimal_odds) * 100
        edge = win_probability - implied_prob
        
        # Display results
        if ev > 0:
            st.success(f"This is a +EV bet with expected return of {ev_percent:.2f}%")
        else:
            st.error(f"This is a -EV bet with expected return of {ev_percent:.2f}%")
        
        # Display metrics
        st.metric("Your Estimated Probability", f"{win_probability:.1f}%")
        st.metric("Implied Probability from Odds", f"{implied_prob:.1f}%")
        st.metric("Edge", f"{edge:.1f}%")
        
        # Kelly calculation if enabled
        if use_kelly:
            st.subheader("Recommended Bet Size")
            
            kelly_bet = ((win_probability/100 * decimal_odds) - 1) / (decimal_odds - 1)
            kelly_bet = max(0, kelly_bet)  # Ensure non-negative
            recommended_bet = kelly_bet * kelly_fraction * bankroll
            
            st.metric("Kelly Percentage", f"{kelly_bet*100:.2f}%")
            st.metric("Adjusted Kelly", f"{(kelly_bet*kelly_fraction*100):.2f}%")
            st.metric("Recommended Bet", f"${recommended_bet:.2f}")
            
            potential_profit = recommended_bet * (decimal_odds - 1)
            st.metric("Potential Profit", f"${potential_profit:.2f}")
    
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Create tabs for additional content
tab1, tab2 = st.tabs(["Bet History", "Learning Center"])

with tab1:
    st.subheader("Bet History")
    
    # Basic bet tracking
    if st.button("Save This Bet"):
        try:
            # Try to load existing bets
            try:
                bets_df = pd.read_csv("bet_history.csv")
            except:
                bets_df = pd.DataFrame(columns=["Date", "Event", "Odds", "Probability", "EV%", "Stake"])
            
            # Add new bet
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
            st.success("Bet saved successfully!")
        except Exception as e:
            st.error(f"Could not save bet: {e}")
    
    # Try to display history
    try:
        bets_df = pd.read_csv("bet_history.csv")
        if not bets_df.empty:
            st.dataframe(bets_df)
        else:
            st.info("No bets recorded yet.")
    except:
        st.info("No bet history found.")

with tab2:
    st.subheader("Learning Center")
    
    st.markdown("""
    ## Understanding Expected Value (EV)
    
    Expected Value (EV) is the average outcome of a bet if placed many times. A positive EV bet means you expect profit long-term.
    
    ### Formula: EV = (Decimal Odds × Win Probability) - 1
    
    Example:
    - Odds: +150 (decimal: 2.5)
    - Your probability: 45%
    - EV = (2.5 × 0.45) - 1 = 0.125 or 12.5%
    
    ### Kelly Criterion
    
    Formula to determine optimal bet size: (p × b - q) / b
    Where:
    - p = probability of winning
    - q = probability of losing (1 - p)
    - b = decimal odds - 1
    
    ### Finding Your Edge
    
    Edge = Your Probability - Implied Probability
    
    Implied Probability from odds = 1 / Decimal Odds
    """)

# Simple footer
st.markdown("---")
st.write("Note: This tool is for educational and entertainment purposes only.")
