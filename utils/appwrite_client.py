from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.account import Account
from appwrite.exception import AppwriteException
import streamlit as st
from appwrite.query import Query
# Initialize Appwrite Client
client = Client()
client.set_endpoint("https://cloud.appwrite.io/v1")  # Appwrite Cloud Endpoint
client.set_project("66572e9c001c02d8c4b0")  # Your Project ID

account = Account(client)
# Initialize Databases Service
databases = Databases(client)

DATABASE_ID = "6740bd070012dba44634"  # Your Database ID
COLLECTION_ID = "6740bd170025d2f7e65f"  # Your Collection ID

def follow_stock(user, stock_name, stock_ticker):
      # Combine user_id and stock_ticker for uniqueness
    data = {
        'user_id': user,
        'stock_name': stock_name,
        'stock_ticker': stock_ticker,
    }
    try:
        response = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            document_id="unique()",
            data=data
        )
        return response
    except AppwriteException as e:
        print(f"Error following stock: {e}")
        return None

def fetch_followed_stocks(user_id):
    try:
        # Query the database to get all stocks followed by the user
        response = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            queries=[
                Query.equal("user_id", user_id)
            ]
        )
        # Extract the stock names and tickers from the response
        stocks = [
            {"stock_name": doc["stock_name"], "stock_ticker": doc["stock_ticker"]}
            for doc in response["documents"]  # Access the 'documents' key from the dictionary
        ]
        return stocks
    except Exception as e:
        st.error(f"Error fetching followed stocks: {e}")
        return []












