import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_moneycontrol_corporate_actions():
    corporate_actions = []
    
    # Different MoneyControl Corporate Actions URLs for different types
    urls = {
        'Dividends': 'https://www.moneycontrol.com/stocks/marketinfo/dividends_declared/index.php',
        'Bonus': 'https://www.moneycontrol.com/stocks/marketinfo/bonus/index.php',
        'Splits': 'https://www.moneycontrol.com/stocks/marketinfo/splits/index.php',
        'Rights': 'https://www.moneycontrol.com/stocks/marketinfo/rights/index.php'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    for action_type, url in urls.items():
        try:
            # Add debug information
            st.write(f"Fetching {action_type} from {url}")
            
            session = requests.Session()
            response = session.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main table
            table = soup.find('table', {'class': 'b_12'})
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cols = row.find_all('td')
                    
                    if action_type == 'Dividends' and len(cols) >= 7:
                        corporate_actions.append({
                            'Company': cols[0].text.strip(),
                            'Type': 'Dividend',
                            'Details': f"{cols[1].text.strip()} - {cols[2].text.strip()}",
                            'Ex-Date': cols[3].text.strip(),
                            'Record Date': cols[4].text.strip(),
                            'Announcement Date': cols[5].text.strip()
                        })
                    
                    elif action_type == 'Bonus' and len(cols) >= 6:
                        corporate_actions.append({
                            'Company': cols[0].text.strip(),
                            'Type': 'Bonus',
                            'Details': f"Ratio: {cols[1].text.strip()}",
                            'Ex-Date': cols[2].text.strip(),
                            'Record Date': cols[3].text.strip(),
                            'Announcement Date': cols[4].text.strip()
                        })
                    
                    elif action_type == 'Splits' and len(cols) >= 6:
                        corporate_actions.append({
                            'Company': cols[0].text.strip(),
                            'Type': 'Split',
                            'Details': f"From {cols[1].text.strip()} to {cols[2].text.strip()}",
                            'Ex-Date': cols[3].text.strip(),
                            'Record Date': cols[4].text.strip(),
                            'Announcement Date': cols[5].text.strip()
                        })
                    
                    elif action_type == 'Rights' and len(cols) >= 6:
                        corporate_actions.append({
                            'Company': cols[0].text.strip(),
                            'Type': 'Rights',
                            'Details': f"Ratio: {cols[1].text.strip()}",
                            'Ex-Date': cols[2].text.strip(),
                            'Record Date': cols[3].text.strip(),
                            'Announcement Date': cols[4].text.strip()
                        })
            
            # Add debug information
            st.write(f"Found {len(corporate_actions)} actions for {action_type}")
            
        except Exception as e:
            st.error(f"Error fetching {action_type}: {str(e)}")
            continue
    
    # Show raw data for debugging
    if corporate_actions:
        st.write("Raw data sample:")
        st.write(corporate_actions[:5])
    else:
        st.write("No corporate actions found")
    
    return pd.DataFrame(corporate_actions)

def filter_relevant_actions(df, stock_list):
    """Filter corporate actions for the given stock list"""
    filtered_actions = []
    
    # Add debug information
    st.write("Filtering actions for stocks:")
    st.write(stock_list)
    
    for _, row in df.iterrows():
        company = row['Company'].upper()
        
        for stock in stock_list:
            stock = stock.upper()
            # More flexible matching
            if (stock in company) or (company in stock):
                filtered_actions.append(row)
                st.write(f"Match found: {stock} in {company}")
                break
                
    return pd.DataFrame(filtered_actions)

# Rest of the code remains the same as in the previous version

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
                        # Sort by Ex-Date
                        filtered_df['Ex-Date'] = pd.to_datetime(filtered_df['Ex-Date'], errors='coerce')
                        filtered_df = filtered_df.sort_values('Ex-Date')
                        filtered_df['Ex-Date'] = filtered_df['Ex-Date'].dt.strftime('%Y-%m-%d')
                        
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
                        
                    else:
                        st.warning("No corporate actions found for the given stocks.")
                else:
                    st.warning("No corporate actions data available at the moment.")
        else:
            st.error("Please enter at least one stock symbol.")

if __name__ == "__main__":
    main()