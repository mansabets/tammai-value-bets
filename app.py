
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime

# App configuration
st.set_page_config(
    page_title="AI Sports Betting Value Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for advanced settings
with st.sidebar:
    st.title("⚙️ Advanced Settings")
    
    # Bankroll management
    st.subheader("Bankroll Management")
    bankroll = st.number_input("Your Bankroll ($)", min_value=0.0, value=1000.0, step=100.0)
    
    # Kelly Criterion settings
    use_kelly = st.checkbox("Use Kelly Criterion for bet sizing", value=True)
    kelly_fraction = st.slider("Kelly Fraction (conservative approach)", 
                              min_value=0.1, max_value=1.0, value=0.5, step=0.1)
    
    # Analysis settings
    st.subheader("Analysis Settings")
    confidence_level = st.slider("Confidence Level (%)", 
                                min_value=50, max_value=99, value=80, step=5)
    
    # Data tracking
    st.subheader("Tracking")
    track_bets = st.checkbox("Track bets for analysis", value=True)
    
    # About section
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool helps you identify positive expected value (+EV) bets and 
    suggests optimal bet sizing using the Kelly Criterion.
    
    **GitHub:** [Your GitHub Repository Link]
    """)

# Main content
st.title("📊 AI Sports Betting Value Tool")
st.write("Estimate whether a bet has positive expected value (EV) and calculate optimal bet sizing.")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["EV Calculator", "Bet History", "Learning Center"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Enter Bet Details:")
        
        # User Inputs with more validation
        odds_format = st.radio("Odds Format:", ["American", "Decimal", "Fractional"], horizontal=True)
        
        if odds_format == "American":
            book_odds = st.number_input("Bookmaker Odds (e.g. +150 or -110)", value=150)
        elif odds_format == "Decimal":
            decimal_odds = st.number_input("Decimal Odds (e.g. 2.50)", value=2.50, min_value=1.01, step=0.01)
        else:  # Fractional
            numerator = st.number_input("Numerator (e.g. 3 for 3/1)", value=3, min_value=1)
            denominator = st.number_input("Denominator (e.g. 1 for 3/1)", value=1, min_value=1)
        
        win_probability = st.slider("Estimated Win Probability (%)", 
                                   min_value=1, max_value=99, value=50)
        
        # Optional fields
        st.markdown("### Optional Details:")
        event_name = st.text_input("Event Name", placeholder="e.g. Lakers vs Warriors")
        bet_type = st.selectbox("Bet Type", ["Moneyline", "Spread", "Over/Under", "Prop", "Parlay"])
        stake = st.number_input("Stake Amount ($)", min_value=0.0, value=0.0, step=10.0)
        
    with col2:
        st.markdown("### EV Analysis:")
        
        # Convert odds to decimal format for calculations
        try:
            if odds_format == "American":
                if book_odds > 0:
                    decimal_odds = (book_odds / 100) + 1
                else:
                    decimal_odds = (100 / abs(book_odds)) + 1
            elif odds_format == "Decimal":
                # Already in decimal format
                pass
            else:  # Fractional
                decimal_odds = (numerator / denominator) + 1
            
            # Calculate EV
            ev = (decimal_odds * (win_probability / 100)) - 1
            ev_percent = ev * 100
            
            # Calculate implied probability from odds
            implied_prob = (1 / decimal_odds) * 100
            edge = win_probability - implied_prob
            
            # Kelly Criterion calculation
            if use_kelly and win_probability > 0:
                kelly_bet = ((win_probability/100 * decimal_odds) - 1) / (decimal_odds - 1)
                kelly_bet = max(0, kelly_bet)  # Ensure non-negative
                recommended_bet = kelly_bet * kelly_fraction * bankroll
            else:
                kelly_bet = 0
                recommended_bet = 0
            
            # Display results
            st.markdown("---")
            
            # Create a visual meter for EV
            if ev > 0:
                st.success(f"### This is a +EV bet with an estimated return of {ev_percent:.2f}%")
                meter_color = "green"
            else:
                st.error(f"### This is a -EV bet with an estimated return of {ev_percent:.2f}%")
                meter_color = "red"
            
            # Create gauge chart for EV visualization
            ev_gauge = px.pie(
                values=[abs(ev_percent), 100-abs(ev_percent)],
                names=["EV", ""],
                hole=0.7,
                color_discrete_sequence=[meter_color, "lightgrey"]
            )
            ev_gauge.update_layout(showlegend=False, height=200, margin=dict(t=0, b=0, l=0, r=0))
            ev_gauge.add_annotation(text=f"{ev_percent:.1f}%", showarrow=False, font_size=20)
            st.plotly_chart(ev_gauge, use_container_width=True)
            
            # Display additional metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Your Estimated Probability", f"{win_probability:.1f}%")
            with col2:
                st.metric("Implied Probability", f"{implied_prob:.1f}%")
            with col3:
                st.metric("Edge", f"{edge:.1f}%", delta=f"{edge:.1f}%")
            
            # Bankroll management
            if use_kelly:
                st.markdown("### Recommended Bet Size:")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Kelly Percentage", f"{kelly_bet*100:.2f}%")
                    st.metric("Adjusted Kelly", f"{(kelly_bet*kelly_fraction*100):.2f}%")
                with col2:
                    st.metric("Recommended Bet", f"${recommended_bet:.2f}")
                    potential_profit = recommended_bet * (decimal_odds - 1)
                    st.metric("Potential Profit", f"${potential_profit:.2f}")
            
            # Save bet button
            if track_bets and st.button("Save Bet"):
                # Load existing bets
                try:
                    bets_df = pd.read_csv("bet_history.csv")
                except:
                    bets_df = pd.DataFrame(columns=["Date", "Event", "Bet Type", "Odds", "Probability", 
                                                  "EV%", "Stake", "Recommended Stake", "Outcome"])
                
                # Append new bet
                new_bet = pd.DataFrame({
                    "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                    "Event": [event_name if event_name else "Unnamed Event"],
                    "Bet Type": [bet_type],
                    "Odds": [decimal_odds],
                    "Probability": [win_probability],
                    "EV%": [ev_percent],
                    "Stake": [stake],
                    "Recommended Stake": [recommended_bet],
                    "Outcome": ["Pending"]
                })
                
                bets_df = pd.concat([bets_df, new_bet], ignore_index=True)
                bets_df.to_csv("bet_history.csv", index=False)
                st.success("Bet saved successfully!")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Please check your inputs and try again.")

with tab2:
    st.markdown("### Bet History")
    
    try:
        bets_df = pd.read_csv("bet_history.csv")
        if not bets_df.empty:
            # Allow user to update bet outcomes
            st.markdown("#### Update Bet Outcomes")
            bet_index = st.selectbox("Select bet to update:", 
                                    options=bets_df.index, 
                                    format_func=lambda x: f"{bets_df.loc[x, 'Date']} - {bets_df.loc[x, 'Event']} ({bets_df.loc[x, 'Outcome']})")
            
            outcome = st.radio("Outcome:", ["Pending", "Won", "Lost", "Pushed", "Canceled"])
            
            if st.button("Update Outcome"):
                bets_df.loc[bet_index, "Outcome"] = outcome
                bets_df.to_csv("bet_history.csv", index=False)
                st.success("Outcome updated!")
            
            # Display bet history
            st.markdown("#### All Bets")
            st.dataframe(bets_df)
            
            # Calculate and display stats
            if len(bets_df[bets_df["Outcome"].isin(["Won", "Lost"])]) > 0:
                st.markdown("#### Betting Stats")
                total_bets = len(bets_df[bets_df["Outcome"].isin(["Won", "Lost"])])
                wins = len(bets_df[bets_df["Outcome"] == "Won"])
                win_rate = (wins / total_bets) * 100
                
                # Calculate profit
                bets_df["Profit"] = 0.0
                for i, row in bets_df.iterrows():
                    if row["Outcome"] == "Won":
                        bets_df.loc[i, "Profit"] = row["Stake"] * (row["Odds"] - 1)
                    elif row["Outcome"] == "Lost":
                        bets_df.loc[i, "Profit"] = -row["Stake"]
                
                total_profit = bets_df["Profit"].sum()
                total_wagered = bets_df[bets_df["Outcome"].isin(["Won", "Lost"])]["Stake"].sum()
                roi = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Bets", total_bets)
                with col2:
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                with col3:
                    st.metric("Total Profit", f"${total_profit:.2f}")
                with col4:
                    st.metric("ROI", f"{roi:.1f}%")
                
                # Create profit chart
                bets_df_completed = bets_df[bets_df["Outcome"].isin(["Won", "Lost"])].copy()
                bets_df_completed["Cumulative Profit"] = bets_df_completed["Profit"].cumsum()
                
                fig = px.line(bets_df_completed, x=bets_df_completed.index, y="Cumulative Profit", 
                             title="Profit Over Time")
                fig.update_layout(xaxis_title="Bet Number", yaxis_title="Cumulative Profit ($)")
                st.plotly_chart(fig, use_container_width=True)
                
                # EV vs Actual Returns
                if "EV%" in bets_df.columns:
                    avg_ev = bets_df_completed["EV%"].mean()
                    actual_roi = roi
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Average Expected Value", f"{avg_ev:.1f}%")
                    with col2:
                        st.metric("Actual ROI", f"{actual_roi:.1f}%", 
                                 delta=f"{actual_roi-avg_ev:.1f}%")
        else:
            st.info("No bets recorded yet. Add some bets to see your history.")
    except Exception as e:
        st.info("No bet history found. Start adding bets to track your performance.")

with tab3:
    st.markdown("### Learning Center")
    
    st.markdown("""
    ## Understanding Expected Value (EV)
    
    Expected Value (EV) is a mathematical concept that represents the average outcome of a bet if it were placed many times. A positive EV (+EV) bet means that, on average, you expect to make money in the long run.
    
    ### How to Calculate EV:
    
    EV = (Decimal Odds × Win Probability) - 1
    
    Example:
    - Bookmaker odds: +150 (decimal: 2.5)
    - Your estimated win probability: 45%
    - EV = (2.5 × 0.45) - 1 = 0.125 or 12.5%
    
    ### Understanding Kelly Criterion
    
    Kelly Criterion is a formula used to determine the optimal size of a series of bets to maximize the logarithm of wealth. It considers your edge and the odds to recommend a bet size.
    
    Kelly Fraction = (p × b - q) / b
    
    Where:
    - p = probability of winning
    - q = probability of losing (1 - p)
    - b = decimal odds - 1
    
    ### Finding Your Edge
    
    Your edge is the difference between your estimated probability and the implied probability from the bookmaker's odds:
    
    Edge = Your Probability - Implied Probability
    
    The implied probability can be calculated from decimal odds:
    Implied Probability = 1 / Decimal Odds
    
    ### Tips for Successful Betting
    
    1. Only bet when you have a positive expected value
    2. Use proper bankroll management (Kelly Criterion)
    3. Track your bets and analyze your performance
    4. Focus on sports/markets where you have an edge
    5. Shop for the best odds across multiple bookmakers
    6. Avoid emotional betting and stick to your strategy
    """)

# Footer
st.markdown("---")
st.caption("Note: This tool is for educational and entertainment purposes only. Gambling involves risk and can be addictive.
