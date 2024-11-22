import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st
import time
from datetime import datetime

# Streamlit Page Setup
st.set_page_config(page_title="Real-Time Candlestick Chart", layout="wide")

# Title
st.title("Microsoft (MSFT) Real-Time Candlestick Chart")

# Sidebar - Interval Selection
interval = st.sidebar.selectbox(
    "Select Interval",
    ["1m", "2m", "5m", "15m", "30m", "1h"],
    index=0
)

# Sidebar - Period Selection
period = st.sidebar.selectbox(
    "Select Period",
    ["1d", "5d", "1mo", "3mo"],
    index=1
)

# Add auto-refresh interval selection
refresh_interval = st.sidebar.slider(
    "Refresh Interval (seconds)",
    min_value=30,
    max_value=300,
    value=60,
    step=30
)

# Function to Fetch Data
@st.cache_data(ttl=60)  # Cache the data for 60 seconds
def fetch_data(ticker, period, interval):
    try:
        return yf.download(tickers=ticker, period=period, interval=interval)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Function to create figure
def create_figure(data):
    fig = go.Figure(data=[go.Candlestick(
        x=data['Datetime'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='MSFT',
        increasing_line_color='green',
        decreasing_line_color='red'
    )])

    # Add volume bars
    fig.add_trace(go.Bar(
        x=data['Datetime'],
        y=data['Volume'],
        name='Volume',
        yaxis='y2',
        marker_color='rgba(128,128,128,0.5)'
    ))

    # Layout customization
    fig.update_layout(
        title={
            'text': f"Microsoft (MSFT) Real-Time Candlestick Chart - Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Time",
        yaxis_title="Price ($)",
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right"
        ),
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=800
    )

    return fig

# Initialize session state for storing the last update time
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Main loop
while True:
    current_time = time.time()
    
    # Check if it's time to update
    if current_time - st.session_state.last_update >= refresh_interval:
        # Fetch updated data
        data = fetch_data("MSFT", period=period, interval=interval)
        
        if data is not None:
            # Reset index to get Datetime column
            data.reset_index(inplace=True)
            
            # Create new figure
            fig = create_figure(data)
            
            # Calculate metrics
            current_price = float(data['Close'].iloc[-1])
            previous_price = float(data['Close'].iloc[-2])
            price_change = ((current_price - previous_price) / previous_price) * 100
            current_volume = int(data['Volume'].iloc[-1])
            day_high = float(data['High'].max())
            day_low = float(data['Low'].min())
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"${current_price:.2f}", f"{price_change:.2f}%")
            with col2:
                st.metric("Volume", f"{current_volume:,}")
            with col3:
                st.metric("Day High", f"${day_high:.2f}")
            with col4:
                st.metric("Day Low", f"${day_low:.2f}")
            
            # Display chart with a unique key
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{current_time}")
            
            # Update last update time
            st.session_state.last_update = current_time
    
    # Add a small delay to prevent excessive CPU usage
    time.sleep(10)

    # Rerun the app
    st.rerun()