import streamlit as st
from GoogleNews import GoogleNews
from transformers import pipeline
import pandas as pd

# Function to fetch stock market and business news data
def fetch_news(keyword, start, count=10):
    googlenews = GoogleNews(lang='en', region='US')
    googlenews.search(keyword)
    googlenews.getpage(1)  # Ensure the first page is fetched
    news_results = googlenews.results()

    for page in range(2, 6):
        googlenews.getpage(page)
        news_results.extend(googlenews.results())

    return news_results[start:start+count]

# AI Sentiment Analysis function
def analyze_sentiment(news_articles):
    # Load sentiment analysis pipeline from Hugging Face
    sentiment_analyzer = pipeline("sentiment-analysis")

    # Analyze sentiment for each article
    sentiment_results = []
    for article in news_articles:
        sentiment = sentiment_analyzer(article['desc'])[0]
        sentiment_results.append((article, sentiment['label'], sentiment['score']))
    
    return sentiment_results

# Function to clean URLs
def clean_url(url):
    # Remove everything starting from '&ved'
    if "&ved" in url:
        url = url.split("&ved")[0]
    return url

# Main function for Streamlit UI
def show_page():
    

    # Title with professional styling
    st.markdown(
        """
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px; text-align: center;">
            <h1 style="color: #000000;">💹 Stock Investor News 💹</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 📰 Get the Latest Stock Market & Business News")

    # Default keyword for fetching news
    default_keyword = "Stock Market"

    # Search bar at the top
    keyword = st.text_input(
        "Search for news (default is 'Stock Market')",
        placeholder="e.g., Apple stock, Tech layoffs, Crypto trends",
        help="Leave blank to use the default topic: 'Stock Market'"
    )

    # Default to predefined topic if the search field is empty
    if not keyword.strip():
        keyword = default_keyword

    if 'news_start' not in st.session_state:
        st.session_state.news_start = 0
    if 'news_data' not in st.session_state:
        st.session_state.news_data = []

    # Fetch News button
    if st.button("🔍 Fetch News"):
        st.session_state.news_start = 0
        st.session_state.news_data = fetch_news(keyword, st.session_state.news_start)
        st.session_state.news_start += 10

    # Display news with AI-powered insights
    if st.session_state.news_data:
        sentiment_results = analyze_sentiment(st.session_state.news_data)
        df = pd.DataFrame(sentiment_results, columns=["Article", "Sentiment", "Score"])

        for index, row in df.iterrows():
            article = row['Article']
            sentiment = row['Sentiment']
            score = row['Score']
            sentiment_text = f"Sentiment: {sentiment} (Confidence: {score:.2f})"
            clean_link = clean_url(article['link'])  # Clean the article link

            # Display the article with sentiment information and cleaned link
            st.markdown(
                f"""
                <div style="background-color: #fff; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #000000;">{index+1}. {article['title']}</h2>
                    <p style="color: #555555;"><strong>Source:</strong> {article['media']} | <strong>Published on:</strong> {article['date']}</p>
                    <p style="color: #000000; font-size: 16px;"><strong>Summary:</strong> {sentiment_text}</p>
                    <p style="color: #000000; font-size: 16px;">{article['desc']}</p>
                    <p style="color: #0000FF;"><a href="{clean_link}" target="_blank">Follow this link</a></p>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button("📥 Load More"):
            additional_news = fetch_news(keyword, st.session_state.news_start)
            if additional_news:
                st.session_state.news_data.extend(additional_news)
                st.session_state.news_start += 10
                sentiment_results = analyze_sentiment(additional_news)
                additional_df = pd.DataFrame(sentiment_results, columns=["Article", "Sentiment", "Score"])

                for index, row in additional_df.iterrows():
                    article = row['Article']
                    sentiment = row['Sentiment']
                    score = row['Score']
                    sentiment_text = f"Sentiment: {sentiment} (Confidence: {score:.2f})"
                    clean_link = clean_url(article['link'])  # Clean the article link

                    st.markdown(
                        f"""
                        <div style="background-color: #e0e0e0; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                            <h2 style="color: #000000;">{len(df) + index + 1}. {article['title']}</h2>
                            <p style="color: #555555;"><strong>Source:</strong> {article['media']} | <strong>Published on:</strong> {article['date']}</p>
                            <p style="color: #000000; font-size: 16px;"><strong>Summary:</strong> {sentiment_text}</p>
                            <p style="color: #000000; font-size: 16px;">{article['desc']}</p>
                            <p style="color: #0000FF;"><a href="{clean_link}" target="_blank">Follow this link</a></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("No more news articles available.")

# Call the show_page function to run the Streamlit app
if __name__ == "__main__":
    show_page()