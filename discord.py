# Importing necessary modules
import nextcord as discord  # Discord API wrapper for Python
import requests  # Module for handling HTTP requests
import json  # Module for handling JSON data
import logging  # Module for logging application events
import os  # Module for interacting with the operating system
from dotenv import load_dotenv  # Module for loading environment variables from a .env file

load_dotenv()  # Loading environment variables

# Retrieving environment variables for bot token, API key, and base URL
bot_token = os.getenv('BOT_TOKEN')  # The bot token for your Discord bot
api_key = os.getenv('API_KEY')  # The API key for the AI service
base_url = os.getenv('BASE_URL', 'https://api.personal.ai/v1/message')  # The base URL for the AI service

print(f'Bot token: {bot_token}')
print(f'API key: {api_key}')
print(f'Base URL: {base_url}')

# Setting up logging
logging.basicConfig(level=logging.INFO)

# Defining intents - Intents dictate what events a bot can "listen" for
intents = discord.Intents.default()  # Get the default Intents object, which includes all intents
intents.messages = True  # Allow the bot to receive message events
intents.message_content = True  # Allow the bot to view message content
client = discord.Client(intents=intents)  # Create a new Client object with the defined intents

def get_ai_response(message):
    headers = {  # Define headers for the API request
        'Content-Type': 'application/json',
        'x-api-key': api_key  # Inserting the API key
    }

    message_data = {  # Define the data to send with the request
        'Text': str(message)
    }

    # Log the request
    print(f'Sending request to {base_url} with data {message_data}')

    try:
        # Send a POST request to the API
        response = requests.post(base_url, headers=headers, json=message_data, timeout=60)
        response.raise_for_status()  # If the request fails, this will raise an exception
        response_json = response.json()  # Convert the response to JSON format
        print(f'AI response: {json.dumps(response_json, indent=2)}')
        return response_json.get('ai_message', '')  # Return the 'ai_message' from the response
    except requests.HTTPError as http_err:  # If a HTTP error occurred, log the error and return a message
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:  # If an error occurred, log the error and return a message
        print(f'Other error occurred: {err}')
    return 'Sorry, an error occurred while processing your request.'

@client.event
async def on_ready():
    # This function runs when the bot has connected to the Discord server
    print(f'Logged in as {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print('------')

@client.event
async def on_message(message):
    # This function runs every time a message is received

    if message.author == client.user:
        return  # If the message is from the bot itself, ignore it

    # Print details about the message
    channel_name = message.channel.name if not isinstance(message.channel, discord.DMChannel) else 'Direct Message'
    print(f'Received message from {message.author.name} in {channel_name}: {message.content}, {message.attachments}, {message.embeds}, {message.mentions}, {message.mention_everyone}, {message.role_mentions}, {message.reactions}')

    # Print details about the message type
    print(f'Message type: {message.type}')
    print(f'Message system content: "{message.system_content}"')
    if message.type == discord.MessageType.thread_created:
        print(f'Thread: {message.thread}')

    # If the message is not a default message, ignore it
    if message.type != discord.MessageType.default:
        print(f'Non-default message type: {message.type}')
        return

    # Print details about the raw message content
    print(f'Raw message content: "{message.content}"')
    content = message.content.strip()  # Remove leading/trailing whitespace
    print(f'Stripped message content: "{content}"')

    # Print details about the message author
    print(f'Author ID: {message.author.id}, Discriminator: {message.author.discriminator}, Is bot: {message.author.bot}')
    
    # Print details about the message itself
    print(f'Message ID: {message.id}, Edited at: {message.edited_at}, Pinned: {message.pinned}')
    print(f'Channel ID: {message.channel.id}, Channel type: {message.channel.type}')

    if not isinstance(message.channel, discord.DMChannel):
        # If the message was not a DM, print details about the guild
        print(f'Guild ID: {message.guild.id}, Guild name: {message.guild.name}')

    # Print details about any reactions to the message
    for reaction in message.reactions:
        print(f'Reaction: {reaction.emoji}, Count: {reaction.count}, Me: {reaction.me}')
        
    if not content:
        print('Message content is empty after stripping.')
        return

    response = get_ai_response(content)  # Get a response from the AI

    if not response:
        print('AI response is empty.')
        return

    print(f'Sending message: {response}')
    await message.channel.send(response)  # Send the response as a message

client.run(bot_token)  # Connect the bot to the Discord server
