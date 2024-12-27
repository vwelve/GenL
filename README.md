# Eventbrite to Discord Event Bot

This project uses a Discord bot to automatically fetch events from Eventbrite and post them to Discord channels. It allows tracking multiple Eventbrite URLs and posting to different channels.

## Features

- Track multiple Eventbrite event pages simultaneously
- Post event details to Discord channels including:
  - Event name and description
  - Start and end times
  - Event image (if available)
  - Direct link to event
- Tracks processed events in SQLite database to avoid duplicates
- Discord bot commands for managing tracked URLs
- Support for tracking different URLs in different channels

## Prerequisites

- Python 3.7+
- Discord Bot Token
- Required Python packages (see requirements.txt)

## Installation & Setup

### Using venv (Python Virtual Environment)

1. Clone the repository:
   ```bash
   git clone https://github.com/vwelve/GenL.git
   cd GenL
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the application:
   - Copy `.env.example` to `.env`
   - Add your Discord bot token to `.env`
   - Adjust any other settings as needed

## Usage

1. Start the bot:
   ```bash
   python main.py
   ```

2. Bot Commands:
   - `!track <url> [#channel]` - Start tracking an Eventbrite URL in specified channel
   - `!untrack <url> [#channel]` - Stop tracking a URL in specified channel
   - `!list_tracking [#channel]` - List all tracked URLs (optionally for specific channel)

3. The bot will:
   - Check tracked Eventbrite URLs every 30 minutes
   - Post new events to respective Discord channels
   - Store processed events in the local database

## Production Deployment

### Using PM2 (Process Manager)

1. Install PM2:
   ```bash
   npm install -g pm2
   ```

2. Start the application:
   ```bash
   pm2 start main.py --name "eventbrite-discord-bot"
   pm2 startup
   pm2 save
   ```

The bot will now run in the background and restart automatically on system boot.

## Configuration

The following environment variables can be set in `.env`:

- `BOT_TOKEN`: Your Discord bot token (required)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.




