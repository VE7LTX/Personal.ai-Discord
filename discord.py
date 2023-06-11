import discord
import requests
import json
import logging

import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL', 'https://api.personal.ai/v1/message')

print(f'Bot token: {bot_token}')
print(f'API key: {api_key}')
print(f'Base URL: {base_url}')

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL', 'https://api.personal.ai/v1/message')
command_prefix = '!chat'

client = discord.Client(intents=intents)

def get_ai_response(message):
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    message_data = {
        'Text': str(message)
    }

    print(f'Sending request to {base_url} with data {message_data}')

    try:
        response = requests.post(base_url, headers=headers, json=message_data, timeout=60)
        response.raise_for_status()
        response_json = response.json()
        print(f'AI response: {json.dumps(response_json, indent=2)}')
        return response_json.get('ai_message', '')
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}')
    return 'Sorry, an error occurred while processing your request.'

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel_name = message.channel.name if not isinstance(message.channel, discord.DMChannel) else 'Direct Message'
    print(f'Received message from {message.author.name} in {channel_name}: {message.content}, {message.attachments}, {message.embeds}, {message.mentions}, {message.mention_everyone}, {message.role_mentions}, {message.reactions}')

    print(f'Raw message content: "{message.content}"')  # Print the raw message content
    content = message.content.strip()
    print(f'Stripped message content: "{content}"')  # Print the stripped message content

    print(f'Author ID: {message.author.id}, Discriminator: {message.author.discriminator}, Is bot: {message.author.bot}')
    print(f'Message ID: {message.id}, Edited at: {message.edited_at}, Pinned: {message.pinned}')
    print(f'Channel ID: {message.channel.id}, Channel type: {message.channel.type}')

    if not isinstance(message.channel, discord.DMChannel):
        print(f'Guild ID: {message.guild.id}, Guild name: {message.guild.name}')

    for reaction in message.reactions:
        print(f'Reaction: {reaction.emoji}, Count: {reaction.count}, Me: {reaction.me}')
        
    if not content:
        print('Message content is empty after stripping.')
        return

    response = get_ai_response(content)

    if not response:
        print('AI response is empty.')
        return

    print(f'Sending message: {response}')
    await message.channel.send(response)

client.run(bot_token)
