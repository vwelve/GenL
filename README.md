# Eventbrite to Discord Event Notifier

This project automatically fetches events from Eventbrite and posts them to a Discord channel via webhooks. It monitors Eventbrite's Los Angeles events page and sends notifications for new upcoming events.

## Features

- Scrapes Eventbrite Los Angeles events page
- Posts event details to Discord including:
  - Event name and description
  - Start and end times
  - Event image (if available)
  - Direct link to event
- Tracks processed events in SQLite database to avoid duplicates
- Implements retry logic and rate limiting for Discord webhooks

## Prerequisites

- Python 3.7+
- Discord webhook URL
- Required Python packages (see requirements.txt)

## Installation & Setup

### Using venv (Python Virtual Environment)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/eventbrite-discord-notifier.git
   cd eventbrite-discord-notifier
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
   - Add your Discord webhook URL to `.env`
   - Adjust any other settings as needed

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. The script will:
   - Check Eventbrite periodically for new events
   - Post new events to your Discord channel
   - Store processed events in the local database

## Production Deployment

### Using PM2 (Process Manager)

1. Install PM2:
   ```bash
   npm install -g pm2
   ```

2. Start the application:
   ```bash
   pm2 start main.py --name "eventbrite-discord"
   pm2 startup
   pm2 save
   ```

The application will now run in the background and restart automatically on system boot.

## Configuration

The following environment variables can be set in `.env`:

- `DISCORD_WEBHOOK_URL`: Your Discord channel webhook URL (required)
- `CHECK_INTERVAL`: Time between Eventbrite checks in minutes (default: 30)
- `DATABASE_PATH`: Path to SQLite database file (default: events.db)
- `MAX_EVENTS`: Maximum number of events to process per check (default: 10)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.




