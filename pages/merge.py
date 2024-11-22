import yfinance as yf
import pandas as pd
import streamlit as st

# Sample sectors and their respective companies' tickers
sectors = {
    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
    'Healthcare': ['JNJ', 'PFE', 'MRK', 'GILD', 'ABBV'],
    'Finance': ['JPM', 'BAC', 'C', 'GS', 'WFC'],
    'Consumer Discretionary': ['DIS', 'HD', 'MCD', 'TSLA', 'NKE'],
    'Energy': ['XOM', 'CVX', 'BP', 'COP', 'SLB'],
}

def fetch_company_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            data.append({
                'Company': info.get('longName', ticker),
                'Ticker': info.get('symbol', ''),
                'Sector': info.get('sector', 'N/A'),
                'Industry': info.get('industry', 'N/A'),
                'Current Price (USD)': info.get('currentPrice', 'N/A'),
                'Market Cap (USD)': info.get('marketCap', 'N/A'),
                'PE Ratio': info.get('trailingPE', 'N/A'),
                'Dividend Yield (%)': info.get('dividendYield', 'N/A'),
                'Free Cash Flow (USD)': info.get('freeCashflow', 'N/A'),
                'Return on Equity (ROE)': info.get('returnOnEquity', 'N/A'),
                'EPS': info.get('epsTrailingTwelveMonths', 'N/A'),
                'Previous Close (USD)': info.get('regularMarketPreviousClose', 'N/A'),
                '52 Week High (USD)': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52 Week Low (USD)': info.get('fiftyTwoWeekLow', 'N/A'),
                'Beta': info.get('beta', 'N/A'),
                'Volume': info.get('volume', 'N/A'),
                'Average Volume (3M)': info.get('averageVolume3Month', 'N/A'),
            })
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}. Error: {e}")
    return pd.DataFrame(data)

def show_main():
    # Title of the app
    st.title('Sector-Based Company Viewer')

    # Dropdown for selecting sector
    sector = st.selectbox('Select a Sector:', list(sectors.keys()))

    if sector:
        st.write(f"Displaying companies in the {sector} sector:")

        # Fetch companies for the selected sector
        companies = sectors[sector]
        company_data = fetch_company_data(companies)

        # Multi-select to choose columns to display
        columns_to_display = st.multiselect(
            'Select columns to display:',
            ['Company', 'Ticker', 'Sector', 'Industry', 'Current Price (USD)', 
             'Market Cap (USD)', 'PE Ratio', 'Dividend Yield (%)', 'Free Cash Flow (USD)', 
             'Return on Equity (ROE)', 'EPS', 'Previous Close (USD)', '52 Week High (USD)', 
             '52 Week Low (USD)', 'Beta', 'Volume', 'Average Volume (3M)'],
            default=['Company', 'Ticker', 'Current Price (USD)', 'Market Cap (USD)']
        )

        # Filter the dataframe based on selected columns
        filtered_data = company_data[columns_to_display]

        # Display the selected data as a table
        if not filtered_data.empty:
            st.dataframe(filtered_data)
        else:
            st.write("No data available for the selected sector.")

# Run the app
if __name__ == "__main__":
    show_main()