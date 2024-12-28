import discord
from datetime import datetime

# Replace webhook functions with Discord message function
async def send_discord_message(channel, event_data, content="New event found!"):
    embed = discord.Embed(
        title=event_data['name'],
        url=event_data['url'],
        description=event_data['summary'],
        color=0x00ff00
    )
    
    start = datetime.fromisoformat(event_data['start_date'].replace('Z', '+00:00'))
    end = datetime.fromisoformat(event_data['end_date'].replace('Z', '+00:00'))
    
    start_str = start.strftime("%A, %b %d %Y %I:%M %p")
    end_str = end.strftime("%A, %b %d %Y %I:%M %p")
    
    embed.set_footer(text=f"Event time: {start_str} - {end_str}")
    
    if 'image' in event_data and event_data['image']['url']:
        embed.set_image(url=event_data['image']['url'])
    
    await channel.send(content=content, embed=embed)