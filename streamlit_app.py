import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_bse_corporate_actions():
    corporate_actions = []
    
    # BSE Corporate Actions URL
    url = "https://www.bseindia.com/markets/MarketInfo/DispNewNoticesCirculars.aspx"
    
    # Headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing corporate actions
        table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gvData'})
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    date_str = cols[0].text.strip()
                    subject = cols[1].text.strip()
                    details = cols[2].text.strip()
                    
                    corporate_actions.append({
                        'Date': date_str,
                        'Subject': subject,
                        'Details': details
                    })
        
    except Exception as e:
        st.error(f"Error fetching BSE data: {str(e)}")
    
    return pd.DataFrame(corporate_actions)

def filter_relevant_actions(df, stock_list):
    """Filter corporate actions for the given stock list"""
    filtered_actions = []
    
    for _, row in df.iterrows():
        subject = row['Subject'].upper()
        details = row['Details'].upper()
        
        for stock in stock_list:
            stock = stock.upper()
            if stock in subject or stock in details:
                filtered_actions.append({
                    'Date': row['Date'],
                    'Stock': stock,
                    'Subject': row['Subject'],
                    'Details': row['Details']
                })
                
    return pd.DataFrame(filtered_actions)

def classify_action_type(subject):
    """Classify the type of corporate action"""
    action_types = {
        'SPLIT': ['SPLIT', 'SUB-DIVISION'],
        'BONUS': ['BONUS'],
        'DIVIDEND': ['DIVIDEND'],
        'RIGHTS': ['RIGHTS'],
        'MERGER': ['MERGER', 'AMALGAMATION'],
        'NAME CHANGE': ['NAME CHANGE', 'SYMBOL CHANGE']
    }
    
    subject = subject.upper()
    for action_type, keywords in action_types.items():
        if any(keyword in subject for keyword in keywords):
            return action_type
    return 'OTHER'

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
    
    # Add date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now())
    with col2:
        end_date = st.date_input("End Date", None)
    
    if st.button("Fetch Corporate Actions"):
        if stocks_list:
            with st.spinner('Fetching corporate actions... This may take a few moments.'):
                # Get all corporate actions from BSE
                df = get_bse_corporate_actions()
                
                if not df.empty:
                    # Filter actions for input stocks
                    filtered_df = filter_relevant_actions(df, stocks_list)
                    
                    if not filtered_df.empty:
                        # Add action type classification
                        filtered_df['Action Type'] = filtered_df['Subject'].apply(classify_action_type)
                        
                        # Convert dates
                        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
                        
                        # Filter by date range if end_date is specified
                        if end_date:
                            filtered_df = filtered_df[
                                (filtered_df['Date'].dt.date >= start_date) & 
                                (filtered_df['Date'].dt.date <= end_date)
                            ]
                        
                        # Sort by date
                        filtered_df = filtered_df.sort_values('Date')
                        
                        # Reset date format for display
                        filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
                        
                        # Reorder columns
                        filtered_df = filtered_df[['Date', 'Stock', 'Action Type', 'Subject', 'Details']]
                        
                        # Display results
                        st.subheader("Upcoming Corporate Actions")
                        st.dataframe(filtered_df, use_container_width=True)
                        
                        # Download option
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="Download Data as CSV",
                            data=csv,
                            file_name="corporate_actions.csv",
                            mime="text/csv"
                        )
                        
                        # Summary statistics
                        st.subheader("Summary")
                        action_type_counts = filtered_df['Action Type'].value_counts()
                        st.write("Corporate Actions by Type:")
                        st.write(action_type_counts)
                        
                    else:
                        st.warning("No corporate actions found for the given stocks in the specified date range.")
                else:
                    st.warning("No corporate actions data available at the moment.")
        else:
            st.error("Please enter at least one stock symbol.")

if __name__ == "__main__":
    main()