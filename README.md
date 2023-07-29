# Discord Bot

This is a Discord bot that interacts with an AI service to generate responses and uploads messages to a memory API. It is built using the Discord.py library.

## Features

- Chat with the bot and receive AI-generated responses.
- Messages are uploaded to a memory API for further analysis.
- Handles multiple server channels.

## Dependencies

- A Personal.ai API Tier Account
- Python 3.7 or higher
- `nextcord` (Discord.py) - Library for Discord integration
- `requests` - Library for making HTTP requests
- `python-dotenv` - Library for loading environment variables

## Installation

1. Clone the repository: `git clone https://github.com/your-username/discord-bot.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set up your environment variables in a `.env` file:
   - `BOT_TOKEN` - Token for your Discord bot
   - `API_KEY` - API key for the AI service and memory API

## Bot Setup

## Usage

1. Invite the bot to your Discord server using an OAuth2 link generated from your discord developer portal.
2. Start the bot by running the `discord.py` script.
3. The bot will listen to messages in the server channels and respond accordingly.
4. Messages will be uploaded to the memory API for analysis.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

Unlicense
