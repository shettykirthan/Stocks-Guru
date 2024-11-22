import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils.appwrite_client import fetch_followed_stocks

# Function to plot the stock chart based on ticker, period, and chart type
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

        # Add different chart types
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

# Stock page function to display stock details
def stock_page():
    # Back button to return to the dashboard
    if st.sidebar.button("Back to Dashboard", key="back_to_dashboard"):
        st.session_state.selected_ticker = None  # Clear the selected stock
        st.session_state.selected_name = None
        st.session_state.user_id = None  # Clear user-related data if necessary
        show_page()  # Call the main dashboard function to show the dashboard again

    st.sidebar.header("Stock Page")
    selected_ticker = st.session_state.get("selected_ticker", "N/A")

    if selected_ticker == "N/A":
        st.error("No stock selected!")
        return

    st.markdown(f"## Details for {selected_ticker}")
    selected_ticker = st.session_state.get('selected_ticker', 'AAPL')
    timespan = st.sidebar.selectbox("Select Time Span", ["1y", "5y", "10y", "Max"])
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Candlestick", "Line", "Mountain"], index=0)

    try:
        stock = yf.Ticker(selected_ticker)
        info = stock.info

        if not info:
            st.error("No information available for the selected stock.")
            return

        # Display stock information
        st.markdown(f"### {info.get('longName', selected_ticker)} Stock Information")
        col1, col2, col3 = st.columns(3)
        col1.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
        col2.metric("PE Ratio", round(info.get('trailingPE', 0), 2))
        col3.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")

        # Plot stock chart
        fig = plot_stock(selected_ticker, timespan, chart_type)
        if fig:
            st.plotly_chart(fig)

        # Display financial data and other details (same as before)
        with st.expander("Company About"):
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

        # Additional financials and recommendations
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

    except Exception as e:
        st.error(f"There is no such stock available, Check Ticker Name")

# Front page function to display followed stocks
def show_page():
    if "username" not in st.session_state or "email" not in st.session_state:
        st.error("You must log in first!")
        st.stop()

    user_id = st.session_state.get("user_id")
    username = st.session_state.username
    email = st.session_state.email

    # Fetch followed stocks from the database
    followed_stocks = fetch_followed_stocks(user_id)

    st.container()
    profile_col1, profile_col2 = st.columns([1, 4])

    with profile_col2:
        st.markdown(f"### {username}")
        st.markdown(f"#### {username}")
        st.markdown(f"**Email**: {email}")

    st.markdown("## Followed Stocks")

    # Display followed stocks as clickable buttons
    for stock in followed_stocks:
        stock_name = stock['stock_name']
        stock_ticker = stock['stock_ticker']

        st.markdown(f"#### {stock_name}")
        st.markdown(f"**Ticker:** {stock_ticker}")

        # Add a unique key for each button
        if st.button(f"View Details for {stock_name} ({stock_ticker})", key=f"view_{stock_ticker}"):
            st.session_state.selected_name = stock_name
            st.session_state.selected_ticker = stock_ticker
            st.session_state.user_id = user_id
            stock_page()  # Navigate to the stock page

if __name__ == "__main__":
    show_page()
