import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import sqlite3
import pytz

# Use BeautifulSoup to parse HTML and extract event IDs
from bs4 import BeautifulSoup

# Use the official API endpoint
URL = 'https://www.eventbrite.ca/d/ca--los-angeles/all-events/'

# Initialize database
def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS processed_events
                 (event_id TEXT PRIMARY KEY, processed_date TIMESTAMP)''')
    conn.commit()
    conn.close()

# Check if event was already processed
def is_event_processed(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM processed_events WHERE event_id = ?', (event_id,))
    result = c.fetchone() is not None
    conn.close()
    return result

# Store processed event
def store_event_id(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    # Convert datetime to ISO format string
    current_time = datetime.now().isoformat()
    c.execute('INSERT INTO processed_events (event_id, processed_date) VALUES (?, ?)',
              (event_id, current_time))
    conn.commit()
    conn.close()

async def send_webhook_with_retry(session, webhook_data, max_retries=5, initial_delay=1):
    webhook_url = 'https://discord.com/api/webhooks/1322003111497170975/NZoxEX5_k-2hbBsSq0uAiFZWMylZhCAJhkEF-RlXZb3S_c9uMG1bvf9WQly5fYFeHy-U'
    delay = initial_delay
    
    for _ in range(max_retries):
        try:
            async with session.post(webhook_url, json=webhook_data) as webhook_response:
                if webhook_response.status == 204:  # Discord returns 204 on success
                    return True
                elif webhook_response.status == 429:  # Rate limit error
                    retry_after_data = await webhook_response.json()
                    wait_time = retry_after_data.get('retry_after', delay)
                    print(f"Rate limited. Server retry_after: {retry_after_data}")
                    print(f"Waiting {wait_time} seconds...")
                    await asyncio.sleep(float(wait_time))
                    delay *= 2  # Exponential backoff
                else:
                    print(f"Failed to send webhook: {webhook_response.status}")
                    await asyncio.sleep(delay)
                    delay *= 2
        except Exception as e:
            print(f"Error sending webhook: {e}")
            await asyncio.sleep(delay)
            delay *= 2
    
    return False

def create_webhook_data(event):
    # Parse start and end dates into datetime objects
    start = datetime.fromisoformat(event['start_date'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(event['end_date'].replace('Z', '+00:00'))
    
    # Format dates in readable format
    start_str = start.strftime("%A, %b %d %Y %I:%M %p")
    end_str = end.strftime("%A, %b %d %Y %I:%M %p")
    
    embed = {
        "title": event['name'],
        "url": event['url'],
        "description": event['summary'],
        "color": 0x00ff00,  # Green color
        "footer": {
            "text": f"Event time: {start_str} - {end_str}"
        }
    }
    
    # Add image if available
    if 'image' in event and event['image']['url']:
        embed["image"] = {"url": event['image']['url']}
    
    return {
        "content": f"Hey @everyone! New post from [Eventbrite]({URL})! Go check it out!",
        "embeds": [embed]
    }

async def fetch_events():
    # Create a ClientSession that persists cookies across requests
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
        # First request
        async with session.get(URL) as response:
            if response.status == 200:
                # Get the HTML content
                html_content = await response.text()
                headers = {}
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find all event card links and extract unique event IDs
                event_links = soup.select('a.event-card-link')
                event_ids = [link.get('data-event-id') for link in event_links if link.get('data-event-id')]
                event_ids = list(set(event_ids))

                # Join event IDs with commas for the API query
                event_ids_param = ','.join(event_ids)
                print('Event IDs:', event_ids)
                print('Number of Event IDs:', len(event_ids))

                # Make API request to get event details
                api_url = f'https://www.eventbrite.ca/api/v3/destination/events/?event_ids={event_ids_param}&page_size=20&expand=event_sales_status,image,primary_venue,saves,ticket_availability,primary_organizer,public_collection'
                async with session.get(api_url, headers=headers) as api_response:
                    if api_response.status == 200:
                        event_data = await api_response.json()
                        # Make timezone-aware datetime objects
                        utc = pytz.UTC
                        current_time = datetime.now(utc)
                        
                        for event in event_data['events']:
                            # Skip if event was already processed
                            if is_event_processed(event['id']):
                                print(f"Event {event['id']} has already been processed")
                                continue

                            print(f'Processing event {event["id"]}')
                                
                            # Parse start date and explicitly make it timezone-aware
                            start_date = datetime.fromisoformat(event['start_date'].replace('Z', '+00:00')).replace(tzinfo=utc)
                            
                            if start_date > current_time:
                                # Create and send webhook
                                webhook_data = create_webhook_data(event)
                                
                                if await send_webhook_with_retry(session, webhook_data):
                                    # Store processed event
                                    store_event_id(event['id'])
                                else:
                                    print(f"Failed to send webhook for event {event['id']} after all retries")
                            else:
                                print(f"Event {event['id']} has already started or passed")
                                print(f"Start date: {start_date}")
                    else:
                        print(f"API request failed with status code: {api_response.status}")
                
            else:
                print(f"Request failed with status code: {response.status}")

# Initialize database and run
init_db()
asyncio.run(fetch_events())
