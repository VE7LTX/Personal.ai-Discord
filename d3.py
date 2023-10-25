# Importing necessary modules
import nextcord as discord
import requests
import json
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
from typing import Tuple, Optional, Union

# Constants
MAX_MEMORY_LENGTH = 64000
base_url = 'https://api.personal.ai/v1/message'
memory_api_url = 'https://api.personal.ai/v1/memory'
DOMAIN_NAME = 'ms-EasyTrainerLaunchLounge'
# Initialize logging
logging.basicConfig(level=logging.DEBUG)


# Load environment variables
load_dotenv()

# Retrieve environment variables
bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('API_KEY')
ai_name = os.getenv('AI_NAME')
server_name = os.getenv('SERVER_NAME')

# Initialize Discord client with all intents
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Global variables
message_memory = ""
session_ids = {}  # Dictionary to store session IDs

def get_ai_response(username: str, message: str, session_id: Optional[str] = None) -> Tuple[str, Union[float, str], str]:
    headers = {'Content-Type': 'application/json', 'x-api-key': api_key}
    
    # Get the current date and time and adjust for Vancouver timezone
    vancouver = pytz.timezone('America/Vancouver')
    current_datetime = datetime.now().astimezone(vancouver).strftime("%Y-%m-%d %H:%M:%S")
    
    # Add it to the context
    context = f"{ai_name}, you are in the Discord server '{server_name}' as of {current_datetime} (Vancouver time)..."
    
    # Prepend the message with the current date and time
    prepended_message = f"{current_datetime} (Vancouver time) {username}>>>: {message}"
    
    payload = {'Text': prepended_message, 'Context': context, 'SessionId': session_id, 'DomainName': DOMAIN_NAME}

    
    logging.info(f"Sending request to AI with payload: {payload}")

    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_data = response.json()
        
        logging.info(f"Received response from AI: {response_data}")

        ai_message = response_data.get('ai_message', '')
        ai_score = float(response_data.get('ai_score', 0))
        new_session_id = response_data.get('SessionId', '')
        
        return ai_message, ai_score, new_session_id
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        logging.debug(f'Full HTTPError exception: {repr(http_err)}')
    except Exception as err:
        logging.error(f'An error occurred: {err}')
        logging.debug(f'Full exception: {repr(err)}')


def upload_memory(text: str, device_name: str = "Discord Server API Connection", created_time: Optional[str] = None):
    headers = {'Content-Type': 'application/json', 'x-api-key': api_key}
    payload = {'Text': text}

    try:
        response = requests.post(memory_api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_json = response.json()
        logging.info(f'Memory API response: {json.dumps(response_json, indent=2)}')
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logging.error(f'Other error occurred: {err}')

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user.name}')
    logging.info(f'Bot ID: {client.user.id}')

@client.event
async def on_message(message):
    global message_memory

    if message.author == client.user:
        return

    content = message.content.strip()
    if not content:
        logging.info('Message content is empty after stripping.')
        return

    session_id = None
    if message.reference:
        session_id = session_ids.get(message.reference.message_id)

    response, ai_score, new_session_id = get_ai_response(message.author.name, content, session_id)

    if not response:
        logging.info('AI response is empty.')
        return

    sent_message = await message.channel.send(f'{response} \nAI Score: {ai_score}')
    session_ids[sent_message.id] = new_session_id

    user_message_details = f"User {message.author.name} said: {content}"
    bot_message_details = f"Bot responded: {response}, AI Score: {ai_score}"
    message_memory += f"{user_message_details}\n{bot_message_details}\n"

    if len(message_memory) > MAX_MEMORY_LENGTH or ai_score > 1:
        upload_memory(message_memory)
        message_memory = ""

# Run the Discord bot
if __name__ == "__main__":
    client.run(bot_token)
