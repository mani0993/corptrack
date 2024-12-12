import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta

def get_corporate_actions(symbols):
    corporate_actions = []
    
    # BSE Corporate Actions
    bse_url = "https://www.bseindia.com/corporates/corporate_act.aspx"
    
    # NSE Corporate Actions
    nse_url = "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
    
    for symbol in symbols:
        try:
            # Using yfinance for basic corporate action data
            stock = yf.Ticker(f"{symbol}.NS")
            
            # Get dividends
            dividends = stock.dividends
            if not dividends.empty:
                for date, amount in dividends.items():
                    if date.date() >= datetime.now().date():
                        corporate_actions.append({
                            'Symbol': symbol,
                            'Action Type': 'Dividend',
                            'Details': f"Amount: ₹{amount}",
                            'Date': date.date()
                        })
            
            # Get stock splits
            splits = stock.splits
            if not splits.empty:
                for date, ratio in splits.items():
                    if date.date() >= datetime.now().date():
                        corporate_actions.append({
                            'Symbol': symbol,
                            'Action Type': 'Stock Split',
                            'Details': f"Ratio: {ratio}:1",
                            'Date': date.date()
                        })
                        
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            continue
            
    return pd.DataFrame(corporate_actions)

def main():
    st.title("Portfolio Corporate Actions Tracker")
    
    # Input area for stock symbols
    st.subheader("Enter Stock Symbols")
    default_stocks = """TARC
ZOMATO
NEULANDLAB
KALYANKJIL
MOTILALOFS
BSE
PGEL
NETWEB
MCX
TRENT
WOCKPHARMA
ANANTRAJ
WABAG
GVT&D
GANESHHOUC
MARKSANS
OFSS
PPLPHARMA
KIRLPNU
JUBLPHARMA
ORCHPHARMA
SHILPAMED
SCHNEIDER
KAYNES
ZENTEC
TIMETECHNO
NATIONALUM
SUPRIYA
DIXON
GRWRHITECH"""
    
    stocks_input = st.text_area("Enter one stock symbol per line:", value=default_stocks, height=300)
    stocks_list = [s.strip() for s in stocks_input.split('\n') if s.strip()]
    
    if st.button("Fetch Corporate Actions"):
        if stocks_list:
            st.info("Fetching corporate actions... This may take a few moments.")
            
            # Get corporate actions
            df = get_corporate_actions(stocks_list)
            
            if not df.empty:
                # Sort by date
                df = df.sort_values('Date')
                
                # Display results
                st.subheader("Upcoming Corporate Actions")
                st.dataframe(df)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name="corporate_actions.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No upcoming corporate actions found for the given stocks.")
        else:
            st.error("Please enter at least one stock symbol.")

if __name__ == "__main__":
    main()