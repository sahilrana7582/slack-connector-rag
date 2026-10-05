import os

from dotenv import load_dotenv
from slack_sdk import WebClient


load_dotenv()

token = os.environ["SLACK_BOT_TOKEN"]

client = WebClient(token=token)

response = client.conversations_list(
    types="public_channel,private_channel",
    limit=100,
)

print(response.data)