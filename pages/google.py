import requests
import streamlit as st
from datetime import datetime

# Function to fetch news using Webz.io API
def fetch_news_from_api(query):
    try:
        api_key = "7ac90d7c-9568-4440-8edf-8c34a75802c4"
        response = requests.get(f"https://api.webz.io/newsApiLite?token={api_key}&q={query}")
        news_data = response.json()
        
        # Extract necessary details
        filtered_news = [
            {
                "title": post.get("title", "No title available"),
                "published": post.get("published", "Unknown date"),
                "link": post.get("url", "#"),
            }
            for post in news_data.get("posts", [])
        ]
        return filtered_news
    except Exception as e:
        st.error(f"An error occurred while fetching news: {e}")
        return []

# Streamlit app for stock news
def show_page():
    # Title with professional styling
    st.markdown(
        """
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;">
            <h1 style="color: #000000;">💹 Stock & Business News 💹</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 📰 Get the Latest News")

    # Search bar for user query
    user_query = st.text_input(
        "Enter a keyword or topic (e.g., Apple, Google, Stock Market)",
        placeholder="Enter a topic to fetch news",
        help="Input a keyword or topic to get the latest news."
    )

    # Fetch and display news when a query is entered
    if user_query.strip():
        st.markdown("### Latest News")
        news_data = fetch_news_from_api(user_query)
        if news_data:
            for index, article in enumerate(news_data):
                # Format published date and time
                published = article['published']
                try:
                    # Convert to datetime object and format
                    dt_object = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S.%f%z")
                    formatted_date_time = dt_object.strftime("%H:%M %d/%m/%Y")  # Format: hour:min date/month/year
                except ValueError:
                    formatted_date_time = "Unknown date"

                st.markdown(
                    f"""
                    <div style="background-color: #262730; padding: 15px; border-radius: 5px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <h4>{index + 1}. {article['title']}</h4>
                        <p><strong>Published:</strong> {formatted_date_time}</p>
                        <p><a href="{article['link']}" target="_blank">Read full article</a></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No news articles available for this query.")

# Run the Streamlit app
if __name__ == "__main__":
    show_page()
