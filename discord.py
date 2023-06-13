"""
Discord Bot

Author: Matthew Schafer / VE7LTX
Company: Diagonal Thinking LTD

Description:
This Discord bot interacts with an AI service to generate responses and uploads messages to a memory API. It utilizes the Discord.py library.

Dependencies:
- nextcord (Discord.py) - Library for Discord integration
- requests - Library for making HTTP requests
- dotenv - Library for loading environment variables

Instructions:
1. Install the required dependencies using pip: `pip install nextcord requests python-dotenv`
2. Set up your environment variables in a .env file:
   - BOT_TOKEN - Token for your Discord bot
   - API_KEY - API key for the AI service and memory API
   - BASE_URL - Base URL for the AI service API (default: 'https://api.personal.ai/v1/message')
   - MEMORY_API_URL - URL for the memory API (default: 'https://api.personal.ai/v1/memory')
3. Run the script: `python discord.py`

"""

# Importing necessary modules
import nextcord as discord
import requests
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Retrieving environment variables
bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL', 'https://api.personal.ai/v1/message')
memory_api_url = os.getenv('MEMORY_API_URL', 'https://api.personal.ai/v1/memory')

# Setting up logging
logging.basicConfig(level=logging.INFO)

# Defining intents
intents = discord.Intents.all()
client = discord.Client(intents=intents)

message_memory = ""

def get_ai_response(message):
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    message_data = {
        'Text': str(message)
    }

    try:
        response = requests.post(base_url, headers=headers, json=message_data, timeout=60)
        response.raise_for_status()
        response_json = response.json()
        ai_message = response_json.get('ai_message', '')
        ai_score = response_json.get('ai_score', '')
        return ai_message, ai_score
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}')
    return 'Sorry, an error occurred while processing your request.', ''

def upload_memory(text, source_name, device_name="API", created_time=None):
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    payload = {
        "Text": text,
        "SourceName": source_name,
        "DeviceName": device_name,
        "CreatedTime": created_time if created_time else None,
    }

    try:
        response = requests.post(memory_api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_json = response.json()
        print(f'Memory API response: {json.dumps(response_json, indent=2)}')
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}')

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print('------')

@client.event
async def on_message(message):
    global message_memory

    if message.author == client.user:
        return

    content = message.content.strip()

    if not content:
        print('Message content is empty after stripping.')
        return

    response, ai_score = get_ai_response(content)

    if not response:
        print('AI response is empty.')
        return

    await message.channel.send(f'{response} \nAI Score: {ai_score}')

    # Accumulate message details for memory
    message_details = f'Received message from {message.author.name}: {message.content}. AI response: {response}. AI Score: {ai_score}.'
    message_memory += message_details + "\n"

    # Check if the accumulated memory exceeds the character limit or the AI score is over +1
    if len(message_memory) > 64000 or ai_score > 1:
        upload_memory(message_memory, "Discord", "Discord Bot")
        message_memory = ""

client.run(bot_token)
