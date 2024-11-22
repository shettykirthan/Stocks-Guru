import yfinance as yf
import pandas as pd
import streamlit as st
import pandas as pd

class YahooFinanceToolSpec:
    """Yahoo Finance tool spec."""
    
    def __init__(self):
        """Initialize the Yahoo Finance tool spec."""
        self.stocks = {}

    def fetch_data(self, tickers: list):
        """Fetch the stock data for multiple tickers."""
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            self.stocks[ticker] = stock
    
    def get_balance_sheet(self, ticker: str) -> pd.DataFrame:
        """Return the balance sheet of the stock."""
        stock = self.stocks.get(ticker)
        if stock is None:
            return pd.DataFrame()
        return stock.balance_sheet.transpose()  # Ensure correct orientation for the dataframe

    def get_income_statement(self, ticker: str) -> pd.DataFrame:
        """Return the income statement of the stock."""
        stock = self.stocks.get(ticker)
        if stock is None:
            return pd.DataFrame()
        return stock.income_stmt.transpose()  # Ensure correct orientation for the dataframe

    def get_cash_flow(self, ticker: str) -> pd.DataFrame:
        """Return the cash flow of the stock."""
        stock = self.stocks.get(ticker)
        if stock is None:
            return pd.DataFrame()
        return stock.cashflow.transpose()  # Ensure correct orientation for the dataframe

    def get_stock_info(self, ticker: str) -> dict:
        """Return the basic info of the stock."""
        stock = self.stocks.get(ticker)
        if stock is None:
            return {}
        return stock.info


# Streamlit app
def app():
    st.title("Compare Stocks Using Yahoo Finance")

    # Input for multiple stock tickers
    tickers = st.text_input("Enter stock tickers separated by commas (e.g., AAPL, MSFT):")
    tickers = [ticker.strip().upper() for ticker in tickers.split(",") if ticker.strip()]

    if tickers:
        finance_tool = YahooFinanceToolSpec()
        finance_tool.fetch_data(tickers)

        # Display available comparison options
        option = st.selectbox(
            "Select Data to Compare:",
            ["Balance Sheet", "Income Statement", "Cash Flow", "Basic Info"]
        )

        # Prepare dataframes for comparison
        if option == "Balance Sheet":
            dfs = {ticker: finance_tool.get_balance_sheet(ticker) for ticker in tickers}
            combined_df = pd.concat(dfs.values(), keys=dfs.keys(), axis=1)
            st.write("Balance Sheet Comparison:")
            st.dataframe(combined_df)
        
        elif option == "Income Statement":
            dfs = {ticker: finance_tool.get_income_statement(ticker) for ticker in tickers}
            combined_df = pd.concat(dfs.values(), keys=dfs.keys(), axis=1)
            st.write("Income Statement Comparison:")
            st.dataframe(combined_df)
        
        elif option == "Cash Flow":
            dfs = {ticker: finance_tool.get_cash_flow(ticker) for ticker in tickers}
            combined_df = pd.concat(dfs.values(), keys=dfs.keys(), axis=1)
            st.write("Cash Flow Comparison:")
            st.dataframe(combined_df)
        
        elif option == "Basic Info":
            info_data = {ticker: finance_tool.get_stock_info(ticker) for ticker in tickers}
            st.write("Basic Info Comparison:")
            st.dataframe(info_data)

if __name__ == "__main__":
    app()