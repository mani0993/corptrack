import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_moneycontrol_corporate_actions():
    corporate_actions = []
    
    # MoneyControl Corporate Actions URL
    url = "https://www.moneycontrol.com/stocks/marketinfo/upcoming_actions/home.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all corporate action tables
        tables = soup.find_all('table', {'class': 'b_12 dvdtbl'})
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    corporate_actions.append({
                        'Company': cols[0].text.strip(),
                        'Purpose': cols[1].text.strip(),
                        'Ex-Date': cols[2].text.strip(),
                        'Record Date': cols[3].text.strip()
                    })
        
    except Exception as e:
        st.error(f"Error fetching corporate actions data: {str(e)}")
        return pd.DataFrame()
    
    return pd.DataFrame(corporate_actions)

def filter_relevant_actions(df, stock_list):
    """Filter corporate actions for the given stock list"""
    filtered_actions = []
    
    for _, row in df.iterrows():
        company = row['Company'].upper()
        
        for stock in stock_list:
            stock = stock.upper()
            if stock in company:
                filtered_actions.append(row)
                break
                
    return pd.DataFrame(filtered_actions)

def classify_action_type(purpose):
    """Classify the type of corporate action"""
    purpose = purpose.upper()
    
    if any(word in purpose for word in ['DIVIDEND', 'DIV']):
        return 'DIVIDEND'
    elif any(word in purpose for word in ['BONUS', 'BON']):
        return 'BONUS'
    elif any(word in purpose for word in ['SPLIT', 'SUB-DIVISION']):
        return 'SPLIT'
    elif any(word in purpose for word in ['RIGHTS']):
        return 'RIGHTS'
    elif any(word in purpose for word in ['MERGER', 'AMALGAMATION']):
        return 'MERGER'
    elif any(word in purpose for word in ['NAME CHANGE', 'SYMBOL']):
        return 'NAME/SYMBOL CHANGE'
    else:
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
    
    if st.button("Fetch Corporate Actions"):
        if stocks_list:
            with st.spinner('Fetching corporate actions... This may take a few moments.'):
                # Get all corporate actions
                df = get_moneycontrol_corporate_actions()
                
                if not df.empty:
                    # Filter actions for input stocks
                    filtered_df = filter_relevant_actions(df, stocks_list)
                    
                    if not filtered_df.empty:
                        # Add action type classification
                        filtered_df['Action Type'] = filtered_df['Purpose'].apply(classify_action_type)
                        
                        # Convert dates
                        for date_col in ['Ex-Date', 'Record Date']:
                            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], format='%d-%m-%Y', errors='coerce')
                        
                        # Sort by Ex-Date
                        filtered_df = filtered_df.sort_values('Ex-Date')
                        
                        # Reset date format for display
                        for date_col in ['Ex-Date', 'Record Date']:
                            filtered_df[date_col] = filtered_df[date_col].dt.strftime('%Y-%m-%d')
                        
                        # Reorder columns
                        filtered_df = filtered_df[['Company', 'Action Type', 'Purpose', 'Ex-Date', 'Record Date']]
                        
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
                        st.warning("No corporate actions found for the given stocks.")
                else:
                    st.warning("No corporate actions data available at the moment.")
        else:
            st.error("Please enter at least one stock symbol.")

if __name__ == "__main__":
    main()