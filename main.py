import aiohttp
import asyncio
import json
from datetime import datetime, timedelta

import pytz
from database import add_tracker, get_all_trackers, init_db, is_event_processed, remove_processed_events, remove_tracker, store_event
import discord
from discord.ext import commands, tasks
from discord.utils import get

# Use BeautifulSoup to parse HTML and extract event IDs
from bs4 import BeautifulSoup

from util import send_discord_message

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use the official API endpoint
URL = 'https://www.eventbrite.ca/d/ca--los-angeles/all-events/'

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Modify fetch_events to work with channels
async def fetch_events_for_url(session, url, channel_id):
    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"Could not find channel {channel_id}")
        return
    
    event_ids = []

    async with session.get(url) as response:
        if response.status == 200:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')

            event_links = soup.select('a.event-card-link')

            for link in event_links:
                event_id = link.get('data-event-id')
                if event_id is not None and event_id not in event_ids:
                    event_ids.append(event_id)
        else:
            print(f"Failed to fetch events for {url}: {response.status}")
    
    event_ids_param = ','.join(event_ids)
    page_size = len(event_ids)

    print('Event IDs:', event_ids)
    print('Number of Event IDs:', len(event_ids))
    
    # Build API URL with query parameters
    api_url = 'https://www.eventbrite.ca/api/v3/destination/events'
    params = {
        'event_ids': event_ids_param,
        'page_size': page_size,
        'expand': 'event_sales_status,image,primary_venue,saves,ticket_availability,primary_organizer,public_collection'
    }
    
    async with session.get(api_url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            events = data['events']

            for event in events:
                if is_event_processed(event['id'], channel_id):
                    print(f"Event {event['id']} already processed")
                    continue
                
                print(f"Processing event {event['id']}")
                timezone = pytz.timezone(event['timezone'])
                start_date_str = f"{event['start_date']} {event['start_time']}"
                start_datetime = timezone.localize(datetime.strptime(start_date_str, "%Y-%m-%d %H:%M"))
                event['start_date'] = start_datetime.isoformat()
                
                end_date_str = f"{event['end_date']} {event['end_time']}"
                end_datetime = timezone.localize(datetime.strptime(end_date_str, "%Y-%m-%d %H:%M"))
                event['end_date'] = end_datetime.isoformat()

                current_time = timezone.localize(datetime.now())

                if start_datetime > current_time:
                    await send_discord_message(channel, event)
                    store_event(event['id'], channel_id)
                else:
                    print(f"Event {event['id']} is in the past")
        else:
            print(f"Failed to fetch events for {api_url}: {response.status}")


@tasks.loop(minutes=30)
async def check_events():
    async with aiohttp.ClientSession() as session:
        trackers = get_all_trackers()
        for url, channel_id in trackers:
            await fetch_events_for_url(session, url, channel_id)

# Bot commands
@bot.command()
@commands.has_permissions(manage_channels=True)
async def track(ctx, url: str, channel: discord.TextChannel = None):
    """
    Add a new Eventbrite URL to track
    Usage: !track <url> [#channel]
    """
    if not url.startswith('https://www.eventbrite'):
        await ctx.send("Please provide a valid Eventbrite URL")
        return
    
    # Use mentioned channel or current channel
    target_channel = channel or ctx.channel
    
    add_tracker(url, target_channel.id)
    await ctx.send(f"Now tracking events from: {url} in {target_channel.mention}")
    
    # Immediately fetch events for the new URL
    async with aiohttp.ClientSession() as session:
        await fetch_events_for_url(session, url, target_channel.id)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def untrack(ctx, url: str, channel: discord.TextChannel = None):
    """
    Stop tracking an Eventbrite URL
    Usage: !untrack <url> [#channel]
    """
    target_channel = channel or ctx.channel
    remove_tracker(url, target_channel.id)
    # Remove processed events for this channel
    remove_processed_events(target_channel.id)
    await ctx.send(f"Stopped tracking: {url} in {target_channel.mention}")

@bot.command()
async def list_tracking(ctx, channel: discord.TextChannel = None):
    """
    List all tracked URLs in a channel
    Usage: !list_tracking [#channel]
    """
    trackers = get_all_trackers()
    
    if channel is not None:
        # Filter for specific channel if provided
        channel_trackers = [url for url, channel_id in trackers if channel_id == channel.id]
        if channel_trackers:
            await ctx.send(f"URLs tracked in {channel.mention}:\n" + "\n".join(channel_trackers))
        else:
            await ctx.send(f"No URLs are being tracked in {channel.mention}")
    else:
        # Show all channels
        tracking_by_channel = {}
        for url, channel_id in trackers:
            if channel_id not in tracking_by_channel:
                tracking_by_channel[channel_id] = []
            tracking_by_channel[channel_id].append(url)
        
        if tracking_by_channel:
            response = "Currently tracked URLs by channel:\n"
            for channel_id, urls in tracking_by_channel.items():
                channel = bot.get_channel(channel_id)
                if channel:
                    response += f"\n{channel.mention}:\n" + "\n".join(f"- {url}" for url in urls) + "\n"
            await ctx.send(response)
        else:
            await ctx.send("No URLs are currently being tracked in any channel.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_events.start()

# Initialize and run
init_db()
bot.run(os.getenv('BOT_TOKEN'))  # Get token from .env file

# Add error handling for permissions
@track.error
@untrack.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need 'Manage Channels' permission to use this command.")
