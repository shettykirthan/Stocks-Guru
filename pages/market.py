import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Set up page config for full-screen experience
st.set_page_config(page_title="Investment Dashboard", page_icon="💹", layout="wide")

# Home Page
import random

def show_page():
    def front_page():
        st.title("Welcome to the Investment Dashboard")
        st.markdown("""
            This dashboard allows you to analyze and track stock, ETF, and mutual fund data.
            You can view charts, financial data, and key metrics to make informed investment decisions.
        """)

    # Select Page
    def select_page():
        st.header("Choose a page:")
        page = st.radio("Select a Page", ("Home", "Stock", "ETF", "Mutual Fund"))
        return page

    # Function to fetch and plot stock data
    def plot_stock(ticker, period, chart_type):
        data = yf.Ticker(ticker).history(period=period, interval="1d")
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

    # Stock Page
    def stock_page():
        selected_ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL")
        timespan = st.selectbox("Select Time Span", ["1y", "5y", "10y", "Max"])
        chart_type = st.selectbox("Select Chart Type", ["Candlestick", "Line", "Mountain"], index=0)
        submit_button = st.button("Submit")

        if submit_button:
            try:
                stock = yf.Ticker(selected_ticker)
                info = stock.info
                st.markdown(f"### {info['longName']} Stock Information")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Market Cap", f"{info['marketCap']:,}")
                col2.metric("PE Ratio", round(info['trailingPE'], 2) if info['trailingPE'] else "N/A")
                col3.metric("52 Week High", f"{info['fiftyTwoWeekHigh']}")

                fig = plot_stock(selected_ticker, timespan, chart_type)
                st.plotly_chart(fig)

                with st.expander("About"):
                    st.markdown(
                        f"""
                        #### {info.get('longName', 'Company')}
                        **Sector:** {info.get('sector', 'N/A')}  
                        **Industry:** {info.get('industry', 'N/A')}  
                        **Business Summary:**  
                        {info.get('longBusinessSummary', 'No information available.')[:250]}...  
                        [Learn more]({info.get('website', '#')})
                        """
                    )

                st.markdown("### Financial Data")

                # Income Statement
                income_statement = stock.financials
                if isinstance(income_statement, pd.DataFrame) and not income_statement.empty:
                    st.subheader("Income Statement")
                    st.dataframe(income_statement)

                # Balance Sheet
                balance_sheet = stock.balance_sheet
                if isinstance(balance_sheet, pd.DataFrame) and not balance_sheet.empty:
                    st.subheader("Balance Sheet")
                    st.dataframe(balance_sheet)

                # Cash Flow
                cash_flow = stock.cashflow
                if isinstance(cash_flow, pd.DataFrame) and not cash_flow.empty:
                    st.subheader("Cash Flow")
                    st.dataframe(cash_flow)

                # Recommendations and Earnings Estimate
                st.markdown("### Stock Recommendations & Earnings Estimate")
                col1, col2 = st.columns(2)

                recommendations = stock.recommendations
                if isinstance(recommendations, pd.DataFrame) and not recommendations.empty:
                    with col1:
                        st.subheader("Stock Recommendations")
                        st.dataframe(recommendations)

                earnings_estimate = stock.earnings_estimate
                if isinstance(earnings_estimate, pd.DataFrame) and not earnings_estimate.empty:
                    with col2:
                        st.subheader("Earnings Estimate")
                        st.dataframe(earnings_estimate)

                # Analyst Price Targets
                analyst_targets = stock.analyst_price_targets
                if isinstance(analyst_targets, pd.DataFrame) and not analyst_targets.empty:
                    st.subheader("Analyst Price Targets")
                    st.dataframe(analyst_targets)

            except Exception as e:
                st.exception(f"An error occurred: {e}")

    # ETF Page
    def etf_page():
        selected_etf = st.text_input("Enter ETF Ticker (e.g., SPY)", value="SPY")
        timespan = st.selectbox("Select Time Span", ["1y", "5y", "10y", "Max"])
        chart_type = st.selectbox("Select Chart Type", ["Line", "Mountain"], index=0)
        submit_button = st.button("Submit")

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
        selected_fund = st.text_input("Enter Mutual Fund Ticker (e.g., VTSAX)", value="VTSAX")
        timespan = st.selectbox("Select Time Span", ["1y", "5y", "10y", "Max"])
        chart_type = st.selectbox("Select Chart Type", ["Line", "Mountain"], index=0)
        submit_button = st.button("Submit")

        if submit_button:
            try:
                mutual_fund = yf.Ticker(selected_fund)
                info = mutual_fund.info

                # Display Mutual Fund info
                st.markdown(f"### {info.get('longName', 'Mutual Fund')} Information")

                # Display Mutual Fund summary and other relevant details
                with st.expander("About"):
                    summary = info.get('summary', 'No information available.')
                    st.markdown(
                        f"""
                        #### {info.get('longName', 'Mutual Fund')}
                        **Category:** {info.get('category', 'N/A')}  
                        **Family:** {info.get('fundFamily', 'N/A')}  
                        **Summary:**  
                        {summary[:250]}...  
                        [Learn more]({info.get('website', '#')})
                        """
                    )

                # Plot the selected Mutual Fund data
                fig = plot_stock(selected_fund, timespan, chart_type)
                st.plotly_chart(fig)

                # Display Historical Data
                historical_data = mutual_fund.history(period=timespan)
                st.subheader(f"Historical Data ({timespan})")
                st.dataframe(historical_data)

            except Exception as e:
                st.exception(f"An error occurred: {e}")

    # Main Program
    if "logged_in" in st.session_state and st.session_state.logged_in:
        page = select_page()
        if page == "Home":
            front_page()
        elif page == "Stock":
            stock_page()
        elif page == "ETF":
            etf_page()
        elif page == "Mutual Fund":
            mutual_fund_page()
if __name__ == "__main__":
    show_page()