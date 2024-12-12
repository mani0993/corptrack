import streamlit as st
import csv
import os
import pytz
from datetime import datetime
import yfinance as yf
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Momentum Portfolio Corporate Actions Tracker",
    page_icon="💹",
    layout="wide"
)

class MomentumPortfolioTracker:
    @staticmethod
    def fetch_upcoming_corporate_actions(symbol):
        """
        Fetch UPCOMING corporate actions for a given stock symbol
        
        :param symbol: Stock symbol to fetch actions for
        :return: Dictionary of UPCOMING corporate actions
        """
        try:
            # Using yfinance to fetch corporate actions
            ticker = yf.Ticker(f"{symbol}.NS")  # Assuming NSE listing
            
            # Get current date with timezone
            today = pd.Timestamp.now(tz='Asia/Kolkata')
            
            # Fetch and filter upcoming actions
            upcoming_actions = {}
            
            # Check Dividends
            dividends = ticker.dividends
            if not dividends.empty:
                # Filter dividends after today
                upcoming_dividends = dividends[dividends.index > today]
                if not upcoming_dividends.empty:
                    upcoming_actions['dividend'] = upcoming_dividends.index[0].strftime('%Y-%m-%d')
            
            # Check Stock Splits (if supported by yfinance)
            splits = ticker.splits
            if not splits.empty:
                # Filter splits after today
                upcoming_splits = splits[splits.index > today]
                if not upcoming_splits.empty:
                    upcoming_actions['split'] = upcoming_splits.index[0].strftime('%Y-%m-%d')
            
            return upcoming_actions
        except Exception as e:
            st.error(f"Error fetching corporate actions for {symbol}: {e}")
            return {}

def save_stocks_to_csv(stocks):
    """
    Save stocks to CSV file
    
    :param stocks: List of stock symbols
    """
    with open('monthly_stocks.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write stocks in a single row
        writer.writerow(stocks)

def load_stocks_from_csv():
    """
    Load stocks from CSV file
    
    :return: List of stock symbols
    """
    try:
        with open('monthly_stocks.csv', 'r') as file:
            reader = csv.reader(file)
            # Take the first row and remove any empty strings
            stocks = [symbol.strip() for symbol in next(reader) if symbol.strip()]
        return stocks
    except (FileNotFoundError, StopIteration):
        return []

def main():
    # Title and description
    st.title("🚀 Momentum Portfolio Corporate Actions Tracker")
    st.write("Track upcoming corporate actions for your monthly momentum portfolio.")

    # Stock Input Section
    st.header("Portfolio Stocks")
    
    # Load existing stocks if any
    existing_stocks = load_stocks_from_csv()
    
    # Text input for stocks
    stock_input = st.text_input(
        "Enter stock symbols (comma-separated)", 
        value=",".join(existing_stocks)
    )
    
    # Split and clean stock symbols
    stocks = [stock.strip().upper() for stock in stock_input.split(',') if stock.strip()]
    
    # Save stocks button
    if st.button("Save Portfolio"):
        if stocks:
            save_stocks_to_csv(stocks)
            st.success(f"Saved {len(stocks)} stocks to portfolio!")
        else:
            st.warning("Please enter at least one stock symbol.")

    # Corporate Actions Section
    st.header("Upcoming Corporate Actions")
    
    if stocks:
        # Create a progress bar
        progress_bar = st.progress(0)
        
        # Prepare to store results
        corporate_actions_data = []
        
        # Fetch corporate actions with progress tracking
        for i, symbol in enumerate(stocks):
            # Update progress bar
            progress_bar.progress((i + 1) / len(stocks))
            
            # Fetch corporate actions
            actions = MomentumPortfolioTracker.fetch_upcoming_corporate_actions(symbol)
            
            # Prepare row for dataframe
            if actions:
                for action_type, date in actions.items():
                    corporate_actions_data.append({
                        'Stock': symbol,
                        'Action Type': action_type.capitalize(),
                        'Date': date
                    })
        
        # Complete progress
        progress_bar.empty()
        
        # Display results
        if corporate_actions_data:
            # Create DataFrame
            df = pd.DataFrame(corporate_actions_data)
            
            # Display as table
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No upcoming corporate actions found for the current portfolio.")
    else:
        st.warning("Please enter stock symbols to track corporate actions.")

    # Additional Information
    st.sidebar.header("ℹ️ About")
    st.sidebar.info(
        "- Track corporate actions for your monthly momentum portfolio\n"
        "- Enter stock symbols separated by commas\n"
        "- Data sourced from Yahoo Finance (NSE)\n"
        "- Refresh monthly for updated portfolio"
    )

# Directly call main()
main()