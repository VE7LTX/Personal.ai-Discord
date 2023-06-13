"""
Discord Bot for Easytrain.ai Platform
Author: Matthew Schafer (VE7LTX), Diagonal Thinking Ltd.

This Python script interacts with the Discord API and the Easytrain.ai platform
to log messages and process them through AI.

Key functionalities:

1. Connects to Discord using the bot token and sets up a client to listen for 
   new messages across all channels that the bot has access to.

2. When a new message is detected, the bot creates a log entry for it. This log 
   includes metadata such as the message ID, channel, type, content, the author's 
   details, timestamps, and other details that could be relevant.

3. This log entry is stored in an activity cache, which temporarily holds multiple 
   log entries before they are sent to the memory API.

4. The bot then sends the user's message to the AI API. It uses the log entry as 
   context for the AI, which helps it understand the conversation's context.

5. If the AI API is available, it processes the message and returns a response 
   that the bot then sends back to the Discord chat.

6. If the AI API is down, the bot handles the exception and retries the request 
   up to 5 times with exponential backoff. It also logs the exception and sends 
   a message to the Discord chat to indicate that the API is down.

7. After the response has been sent, or if an exception occurred, the bot sends 
   the activity cache to the memory API. It divides the cache into chunks that 
   are small enough for the API to handle.

8. In addition, the bot listens for errors on other events. If an error occurs, 
   it writes it to a file for later review.

The script uses these third-party Python libraries:
- nextcord: for Discord API interaction
- requests: for making HTTP requests to the AI API and memory API
- json: for JSON data handling
- logging: for logging events and errors
- os and dotenv: for handling environment variables securely
- retrying: for retrying requests to the AI API

The bot uses environment variables to securely handle sensitive information, 
such as the bot token and the AI API key.

Created on: June 12, 2023
"""


import nextcord as discord
import requests
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from retrying import retry

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL', 'https://api.personal.ai/v1/message')
memory_api_url = os.getenv('MEMORY_API_URL', 'https://api.personal.ai/v1/memory')

logging.basicConfig(level=logging.INFO)

activity_cache = []

# Create a new Discord client with all intents enabled
intents = discord.Intents.all()
client = discord.Client(intents=intents)

def create_log_entry(message):
    log_entry = {
        "timestamp": str(datetime.now()),
        "message_id": message.id,
        "channel_name": str(message.channel.name if not isinstance(message.channel, discord.DMChannel) else 'Direct Message'),
        "message_type": str(message.type),
        "message_content": message.content,
        "message_system_content": message.system_content,
        "message_stripped_content": message.content.strip(),
        "author_id": message.author.id,
        "author_name": message.author.name,
        "author_discriminator": message.author.discriminator,
        "author_is_bot": message.author.bot,
        "message_edited_at": str(message.edited_at),
        "message_pinned": message.pinned,
        "channel_id": message.channel.id,
        "channel_type": str(message.channel.type),
        "guild_id": message.guild.id if not isinstance(message.channel, discord.DMChannel) else None,
        "guild_name": message.guild.name if not isinstance(message.channel, discord.DMChannel) else None,
        "message_attachments": [str(attachment.to_dict()) for attachment in message.attachments],
        "message_embeds": [str(embed.to_dict()) for embed in message.embeds],
        "message_mentions": [str(mention.to_dict()) for mention in message.mentions],
        "message_mention_everyone": message.mention_everyone,
        "message_role_mentions": [str(role_mention.to_dict()) for role_mention in message.role_mentions],
        "message_reactions": [str(reaction.to_dict()) for reaction in message.reactions],
        "DeviceName": "Discord",
        "RawFeedText": message.content.strip()
    }
    return log_entry

def send_to_memory_api():
    global activity_cache
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    while activity_cache:
        memory_text = ''
        while activity_cache and len(memory_text) + len(json.dumps(activity_cache[0])) <= 64000:
            memory_text += json.dumps(activity_cache.pop(0)) + '\n'
        data = {
            'Text': memory_text.strip(),
            'SourceName': 'Discord Bot',
            'CreatedTime': str(datetime.now()),
            'DeviceName': 'Discord',
            'RawFeedText': memory_text.strip()
        }
        response = requests.post(memory_api_url, headers=headers, json=data)
        logging.info(f'Sent memory to memory API: {response.text}')

@retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def send_to_ai_api(data, headers):
    response = requests.post(base_url, headers=headers, json=data)
    logging.info(f'Sent message to AI API: {data}')
    logging.info(f'Received response from AI API: {response.text}')
    if response.status_code != 200:
        logging.error(f'Error: AI API returned status code {response.status_code}')
    return response

@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    log_entry = create_log_entry(message)
    activity_cache.append(log_entry)

    logging.info(f'Received message from {message.author}: {message.content}')

    data = {
        'context': json.dumps(log_entry, default=str),
        'message': message.content
    }

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    try:
        response = send_to_ai_api(data, headers)
        response_data = response.json()
        ai_message = response_data.get('ai_message')
        ai_score = response_data.get('score')  # Extract score from the response
        await message.channel.send(f'{ai_message}\nAI confidence score: {ai_score}')
        send_to_memory_api()
    except Exception as e:
        logging.error(f'Error: {e}')
        await message.channel.send('API Down. RETRYING...')

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(bot_token)
