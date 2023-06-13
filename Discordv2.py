import os

import requests

import json

import nextcord as discord

from dotenv import load_dotenv

# Load environment variables from .env file

load_dotenv()

# Retrieve environment variables

bot_token = os.getenv('BOT_TOKEN')

openai_api_key = os.getenv('OPENAI_API_KEY')

api_key = os.getenv('API_KEY')

base_url = os.getenv('BASE_URL', 'https://api.personal.ai/v1/message')

memory_api_url = os.getenv('MEMORY_API_URL', 'https://api.personal.ai/v1/memory')

# Define intents for Discord client

intents = discord.Intents.all()

client = discord.Client(intents=intents)

# Initialize message memory

message_memory = ""

def get_ai_response(message):

    # Define headers for OpenAI API request

    headers = {

        'Content-Type': 'application/json',

        'Authorization': f'Bearer {openai_api_key}'

    }

    # Define data for OpenAI API request

    message_data = {

        'model': 'gpt-3.5-turbo',

        'messages': [

            {"role": "system", "content": "You are an assistant interpreting a Discord chat thread. Identify and list the topics related to the conversation."},

            {"role": "user", "content": message.content},

            {"role": "assistant", "content": message.content}

        ]

    }

    try:

        # Make API request to OpenAI

        response = requests.post('https://api.openai.com/v1/engines/davinci-codex/completions', headers=headers, json=message_data, timeout=60)

        response.raise_for_status()

        response_json = response.json()

        ai_message = response_json.get('choices')[0].get('message').get('content')

        print(f'AI response: {ai_message}')  # Debugging print statement

        return ai_message

    except requests.HTTPError as http_err:

        print(f'HTTP error occurred: {http_err}')  

    except Exception as err:

        print(f'Other error occurred: {err}')

    return 'Sorry, an error occurred while processing your request.'

def upload_memory(text, source_name, device_name="API", created_time=None):

    # Define headers for memory API request

    headers = {

        'Content-Type': 'application/json',

        'x-api-key': api_key

    }

    # Define data for memory API request

    payload = {

        "Text": text,

        "SourceName": source_name,

        "DeviceName": device_name,

        "CreatedTime": created_time if created_time else None,

    }

    try:

        # Make API request to memory API

        response = requests.post(memory_api_url, headers=headers, json=payload, timeout=60)

        response.raise_for_status()

        response_json = response.json()

        print(f'Memory API response: {json.dumps(response_json, indent=2)}')  # Debugging print statement

    except requests.HTTPError as http_err:

        print(f'HTTP error occurred: {http_err}') 

    except Exception as err:

        print(f'Other error occurred: {err}')

@client.event

async def on_ready():

    print(f'Logged in as {client.user.name}')  # Debugging print statement

    print(f'Bot ID: {client.user.id}')  # Debugging print statement

    print('-------')

@client.event

async def on_message(message):

    global message_memory

    if message.author == client.userHere's the continuation of the `discordv2.py` script:

```python

        return

    content = message.content.strip()

    if not content:

        print('Message content is empty after stripping.')  # Debugging print statement

        return

    response = get_ai_response(message)

    if not response:

        print('AI response is empty.')  # Debugging print statement

        return

    await message.channel.send(f'{response}')

    # Accumulate message details for memory

    message_details = f'Received message from {message.author.name}: {message.content}. AI response: {response}.'

    print(f'Message details: {message_details}')  # Debugging print statement

    message_memory += message_details + "\n"

    # Check if the accumulated memory exceeds the character limit

    if len(message_memory) > 64000:

        upload_memory(message_memory, "Discord", "Discord Bot")

        message_memory = ""

client.run(bot_token)

