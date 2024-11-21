import streamlit as st


    # Session state check for logged-in user
def show_page():
        if "username" not in st.session_state or "email" not in st.session_state:
            st.error("You must log in first!")
            st.stop()

        # Get the logged-in user's information from session state
        username = st.session_state.username
        email = st.session_state.email
        name = st.session_state.get("username", "User")  # Use the name from session state, or default to "User"

        # Example: Replace with actual user profile data fetching logic if needed
        user_data = {
            "name": name,  # Display the user's name from session state
            "username": username,     # Use the username from the session state
            "email": email            # Use the email from the session state
        }

        # Mock stock data (can be dynamic as well)
        stock_data = [
            {"ticker": "APPLE", "price": 150.25, "company": "Apple Inc.", "change": 2.5},
            {"ticker": "GOOGLE", "price": 2750.80, "company": "Alphabet Inc.", "change": -1.2},
            {"ticker": "MSFT", "price": 305.15, "company": "Microsoft Corporation", "change": 0.8},
            {"ticker": "AMZN", "price": 3380.50, "company": "Amazon.com, Inc.", "change": -0.5},
            {"ticker": "TSLA", "price": 750.30, "company": "Tesla, Inc.", "change": 3.2},
            {"ticker": "FB", "price": 330.75, "company": "Meta Platforms, Inc.", "change": 1.5},
        ]

        # User Profile Section
        st.container()
        profile_col1, profile_col2 = st.columns([1, 4])

        with profile_col2:
            st.markdown(f"### {user_data['name']}")
            st.markdown(f"#### {user_data['username']}")
            st.markdown(f"**Email**: {user_data['email']}")  # Display email from session state

        st.markdown("## Followed Stocks")

        # Stock Cards Layout
        rows = len(stock_data) // 3 + 1
        for i in range(rows):
            cols = st.columns(3)
            for j, stock in enumerate(stock_data[i * 3:(i + 1) * 3]):
                with cols[j]:
                    st.markdown(
                        f"""
                        <div style='border: 1px solid #ccc; padding: 16px; border-radius: 8px; text-align: center;'>
                            <h4>{stock['ticker']}</h4>
                            <p style='font-size: 24px; margin: 8px 0;'>${stock['price']}</p>
                            <p style='font-size: 14px; color: gray;'>{stock['company']}</p>
                            <p style='font-size: 16px; color: {"green" if stock["change"] > 0 else "red"};'>{stock['change']}%</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            
if __name__ == "__main__":
    show_page()
