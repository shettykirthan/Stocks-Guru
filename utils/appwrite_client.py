from appwrite.client import Client
from appwrite.services.account import Account

client = Client()
client.set_endpoint("https://cloud.appwrite.io/v1")
client.set_project("66572e9c001c02d8c4b0")

account = Account(client)





