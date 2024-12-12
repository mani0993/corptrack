import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def get_corporate_actions(symbol):
    try:
        # Append .NS for NSE stocks
        stock = yf.Ticker(f"{symbol}.NS")
        
        # Get all available corporate actions
        actions = pd.DataFrame()
        
        # Get dividends
        dividends = stock.dividends
        if not dividends.empty:
            div_df = pd.DataFrame(dividends)
            div_df['Action'] = 'Dividend'
            div_df['Details'] = 'Amount: ₹' + div_df[0].astype(str)
            actions = pd.concat([actions, div_df])
        
        # Get stock splits
        splits = stock.splits
        if not splits.empty:
            split_df = pd.DataFrame(splits)
            split_df['Action'] = 'Stock Split'
            split_df['Details'] = 'Ratio: ' + split_df[0].astype(str) + ':1'
            actions = pd.concat([actions, split_df])
            
        # Get any other corporate actions if available
        info = stock.info
        if 'lastDividendDate' in info:
            last_div_date = datetime.fromtimestamp(info['lastDividendDate'])
            if last_div_date > datetime.now() - timedelta(days=30):
                next_div = pd.DataFrame({
                    'Date': [last_div_date],
                    'Action': ['Upcoming Dividend'],
                    'Details': [f"Amount: ₹{info.get('lastDividendValue', 'N/A')}"]
                })
                actions = pd.concat([actions, next_div])
        
        if not actions.empty:
            actions['Symbol'] = symbol
            return actions
        
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
    
    return pd.DataFrame()

def main():
    st.title("Portfolio Corporate Actions Tracker")
    
    stocks = """TARC
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
    
    stocks_list = [s.strip() for s in stocks.split('\n') if s.strip()]
    
    if st.button("Fetch Corporate Actions"):
        with st.spinner('Fetching data...'):
            all_actions = pd.DataFrame()
            
            for symbol in stocks_list:
                df = get_corporate_actions(symbol)
                if not df.empty:
                    all_actions = pd.concat([all_actions, df])
            
            if not all_actions.empty:
                # Sort by date
                all_actions = all_actions.sort_values('Date', ascending=False)
                
                # Filter for future dates
                future_actions = all_actions[all_actions['Date'] > datetime.now()]
                
                if not future_actions.empty:
                    st.success(f"Found {len(future_actions)} upcoming corporate actions")
                    st.dataframe(future_actions)
                else:
                    st.info("No upcoming corporate actions found")
                    
                # Show recent past actions as well
                past_actions = all_actions[all_actions['Date'] <= datetime.now()]
                if not past_actions.empty:
                    st.subheader("Recent Past Actions")
                    st.dataframe(past_actions.head())
            else:
                st.warning("No corporate actions found for any stocks")

if __name__ == "__main__":
    main()