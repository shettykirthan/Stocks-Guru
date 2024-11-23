import streamlit as st
import pandas as pd
import os
import yfinance as yf
from utils.appwrite_client import follow_stock
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set up page config for full-screen experience (MUST BE FIRST)
st.set_page_config(page_title="Investment Dashboard", layout="wide")

# Now, you can define the rest of your functions and code
def show_page():
    # Sidebar Input
    st.sidebar.header("Investment Dashboard")
    page = st.sidebar.radio("Select a Page", ("Stocks",  "ETF", "Mutual Fund"))
    # Function to load stock data from CSV
    def load_stock_data():
        csv_path = os.path.join('assets', 'namesandtickernames.csv')
        try:
            data = pd.read_csv(csv_path)
            if data.empty:
                st.warning("The stock data file is empty.")
                return pd.DataFrame(columns=['Ticker', 'Name'])
            return data
        except FileNotFoundError:
            st.error(f"File not found: {csv_path}")
            return pd.DataFrame(columns=['Ticker', 'Name'])
        except pd.errors.EmptyDataError:
            st.error("The stock data file is empty or corrupted.")
            return pd.DataFrame(columns=['Ticker', 'Name'])
        except Exception as e:
            st.error(f"Unexpected error loading stock data: {e}")
            return pd.DataFrame(columns=['Ticker', 'Name'])

    # Stock plotting function
    def plot_stock(ticker, period, chart_type):
        try:
            data = yf.Ticker(ticker).history(period=period, interval="1d")
            
            if data.empty:
                st.error(f"No stock data available for ticker: {ticker}")
                return None

            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=[f'{ticker} Stock Price Chart', 'Trading Volume'],
                row_heights=[0.7, 0.3]
            )

            if chart_type == "Candlestick":
                fig.add_trace(
                    go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name="Candlestick"
                    ),
                    row=1, col=1
                )
            elif chart_type == "Line":
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['Close'],
                        mode='lines',
                        name="Close Price",
                        line=dict(color='blue')
                    ),
                    row=1, col=1
                )
            elif chart_type == "Mountain":
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['Close'],
                        fill='tozeroy',
                        mode='lines',
                        name="Close Price",
                        line=dict(color='skyblue')
                    ),
                    row=1, col=1
                )

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'].rolling(window=50).mean(),
                    mode='lines',
                    name="50-Day SMA",
                    line=dict(color='orange')
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'].ewm(span=50).mean(),
                    mode='lines',
                    name="50-Day EMA",
                    line=dict(color='green')
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name="Volume",
                    marker=dict(color='gray')
                ),
                row=2, col=1
            )

            fig.update_layout(
                title=f'{ticker} Stock Data',
                xaxis_title="Date",
                yaxis_title="Price",
                xaxis2_title="Date",
                yaxis2_title="Volume",
                template="plotly_dark",
                hovermode="x unified",
                showlegend=True,
                height=800,
                xaxis_rangeslider_visible=True
            )

            return fig
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None


    # Front page function to display stock list and search
    def front_page():
        st.title("Welcome to the Investment Dashboard")
        st.markdown("""
            This dashboard allows you to analyze and track stock, ETF, and mutual fund data.
            You can view charts, financial data, and key metrics to make informed investment decisions.
        """)

        # Load stock data
        stocks_df = load_stock_data()
        
        if not stocks_df.empty:
            # Search functionality
            st.subheader("Search Stocks")
            
            # Create dropdown with stock suggestions
            stocks_df['Display'] = stocks_df['Name'] + ' (' + stocks_df['Ticker'] + ')'
            sorted_stocks = stocks_df.sort_values('Display')
            
            selected_stock = st.selectbox(
                "Select a Stock", 
                [""] + sorted_stocks['Display'].tolist(),
                format_func=lambda x: "" if x == "" else x
            )
            
            # Process selection
            if selected_stock and selected_stock != "":
                selected_row = stocks_df[stocks_df['Display'] == selected_stock].iloc[0]
                st.session_state.selected_stock_ticker = selected_row['Ticker']
                st.session_state.selected_stock_name = selected_row['Name']
                st.rerun()
        else:
            st.info("No stock data available.")
        
        # Display first 30 stocks
        if not stocks_df.empty:
            st.subheader("Top Stocks")
            
            # Divide stocks into rows of 3 columns
            limited_stocks = stocks_df.head(30)
            rows = [limited_stocks[i:i+3] for i in range(0, len(limited_stocks), 3)]
            
            for row_stocks in rows:
                # Create columns for this row
                cols = st.columns(3)
                
                # Iterate through stocks in this row
                for i, (_, stock) in enumerate(row_stocks.iterrows()):
                    ticker = stock["Ticker"]
                    name = stock["Name"]
                    
                    # Create a styled button in each column
                    with cols[i]:
                        # Use st.container for a boxed look
                        with st.container(border=True):
                            st.markdown(f"#### {name}")
                            st.markdown(f"**Ticker:** {ticker}")
                            
                            # Button styled to look like the whole container is clickable
                            if st.button(f"Select {ticker}", key=ticker):
                                st.session_state.selected_stock_ticker = ticker
                                st.session_state.selected_stock_name = name
                                st.rerun()
        else:
            st.info("No stock data available.")

    # Stock details page 
    def stock_page():
        # Back button to return to front page
        if st.sidebar.button("Back to Stock List"):
            del st.session_state.selected_stock_ticker
            st.rerun()

        st.sidebar.header("Stock Data")
        selected_stock_ticker = st.session_state.get('selected_stock_ticker', 'AAPL')
        timespan = st.sidebar.selectbox("Select Time Span", ["1y", "5y", "10y", "Max"])
        chart_type = st.sidebar.selectbox("Select Chart Type", ["Candlestick", "Line", "Mountain"], index=0)

        try:
            
            selected_stock_name = st.session_state.selected_stock_name
            user_id = st.session_state.user_id
            stock = yf.Ticker(selected_stock_ticker)
            info = stock.info

            if not info:
                st.error("No information available for the selected stock.")
                return

            st.markdown(f"### {info.get('longName', selected_stock_ticker)} Stock Information")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
            col2.metric("PE Ratio", round(info.get('trailingPE', 0), 2))
            col3.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")

            fig = plot_stock(selected_stock_ticker, timespan, chart_type)
            if fig:
                st.plotly_chart(fig)

            if st.button("Follow Stock"):
    # Call the function to follow the stock and add to the Appwrite database
                response = follow_stock(user_id, selected_stock_name, selected_stock_ticker)
                
                if response:
                    st.success("Stock followed successfully!")
                else:
                    st.error("Error following stock.")
                    st.write(response)

            # Company About Section
            with st.expander("About"):
                st.markdown(
                    f"""
                    #### {info.get('longName', 'Company')}
                    **Sector:** {info.get('sector', 'N/A')}  
                    **Industry:** {info.get('industry', 'N/A')}  
                    **Business Summary:**  
                    {info.get('longBusinessSummary', 'No information available.')[:500]}...  
                    [Learn more]({info.get('website', '#')})
                    """
                )

            # Financial Data Sections (same as before)
            st.markdown("### Financial Data")
            income_statement = stock.financials
            if not income_statement.empty:
                st.subheader("Income Statement")
                st.dataframe(income_statement)

            balance_sheet = stock.balance_sheet
            if not balance_sheet.empty:
                st.subheader("Balance Sheet")
                st.dataframe(balance_sheet)

            cash_flow = stock.cashflow
            if not cash_flow.empty:
                st.subheader("Cash Flow")
                st.dataframe(cash_flow)

            st.markdown("### Stock Recommendations & Earnings Estimate")
            col1, col2 = st.columns(2)

            recommendations = stock.recommendations
            if not recommendations.empty:
                with col1:
                    st.subheader("Stock Recommendations")
                    st.dataframe(recommendations)

            earnings_estimate = stock.earnings_estimate
            if isinstance(earnings_estimate, pd.DataFrame) and not earnings_estimate.empty:
                with col2:
                    st.subheader("Earnings Estimate")
                    st.dataframe(earnings_estimate)

            analyst_targets = stock.analyst_price_targets
            if isinstance(analyst_targets, pd.DataFrame) and not analyst_targets.empty:
                st.subheader("Analyst Price Targets")
                st.dataframe(analyst_targets)

        except Exception as e:
            st.error(f"There is no such stock available, Check Ticker Name")
    # ETF Page
    def etf_page():
        st.sidebar.header("ETF Data")
        selected_etf = st.sidebar.text_input("Enter ETF Ticker (e.g., SPY)", value="SPY")
        timespan = st.sidebar.selectbox("Select Time Span", ["1y", "5y", "10y", "Max"])
        chart_type = st.sidebar.selectbox("Select Chart Type", ["Line", "Mountain"], index=0)
        submit_button = st.sidebar.button("Submit")

        if submit_button:
            try:
                etf = yf.Ticker(selected_etf)
                info = etf.info

                # Display ETF info
                st.markdown(f"### {info.get('longName', 'ETF')} Information")

                # Display ETF summary and other relevant details
                with st.expander("About"):
                    summary = info.get('summary', 'No information available.')
                    st.markdown(
                        f"""
                        #### {info.get('longName', 'ETF')}
                        **Category:** {info.get('category', 'N/A')}  
                        **Family:** {info.get('fundFamily', 'N/A')}  
                        **Summary:**  
                        {summary[:250]}...  
                        [Learn more]({info.get('website', '#')})
                        """
                    )

                # Plot the selected ETF data
                fig = plot_stock(selected_etf, timespan, chart_type)
                st.plotly_chart(fig)

                # Display Historical Data
                historical_data = etf.history(period=timespan)
                st.subheader(f"Historical Data ({timespan})")
                st.dataframe(historical_data)

            except Exception as e:
                st.exception(f"An error occurred: {e}")

    # Mutual Funds Page
    def mutual_fund_page():
        st.sidebar.header("Mutual Fund Data")
        selected_fund = st.sidebar.text_input("Enter Mutual Fund Ticker (e.g., VTSAX)", value="VTSAX")
        timespan = st.sidebar.selectbox("Select Time Span", ["1y", "5y", "10y", "Max"])
        chart_type = st.sidebar.selectbox("Select Chart Type", ["Line", "Mountain"], index=0)
        submit_button = st.sidebar.button("Submit")

        if submit_button:
            try:
                mutual_fund = yf.Ticker(selected_fund)
                info = mutual_fund.info

                # Display fund info
                st.markdown(f"### {info.get('longName', 'Mutual Fund')} Information")

                # Display Mutual Fund summary and other relevant details
                with st.expander("About"):
                    summary = info.get('summary', 'No information available.')
                    st.markdown(
                        f"""
                        #### {info.get('longName', 'Fund')}
                        **Category:** {info.get('category', 'N/A')}  
                        **Expense Ratio:** {info.get('expenseRatio', 'N/A')}  
                        **Summary:**  
                        {summary[:250]}...  
                        [Learn more]({info.get('website', '#')})
                        """
                    )

                # Plot the selected mutual fund data
                fig = plot_stock(selected_fund, timespan, chart_type)
                st.plotly_chart(fig)

                # Display Historical Data
                historical_data = mutual_fund.history(period=timespan)
                st.subheader(f"Historical Data ({timespan})")
                st.dataframe(historical_data)

            except Exception as e:
                st.exception(f"An error occurred: {e}")
    def show_page():
        if "selected_stock_ticker" in st.session_state:
            stock_page()
        else:
            front_page()
    if page == "Stocks":
        show_page()
    
    elif page == "ETF":
        etf_page()
    elif page == "Mutual Fund":
        mutual_fund_page()
    
if __name__ == "__main__":
    show_page()
