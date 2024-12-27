import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS processed_events
                 (event_id TEXT PRIMARY KEY, channel_id INTEGER, processed_date TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS event_trackers
                 (url TEXT, channel_id INTEGER, 
                  UNIQUE(url, channel_id))''')
    conn.commit()
    conn.close()

def is_event_processed(event_id, channel_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM processed_events WHERE event_id = ? AND channel_id = ?', (event_id, channel_id))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def store_event(event_id, channel_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO processed_events (event_id, channel_id, processed_date) VALUES (?, ?, ?)',
              (event_id, channel_id, datetime.now()))
    conn.commit()
    conn.close()

# Add functions to manage URLs
def add_tracker(url, channel_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO event_trackers (url, channel_id) VALUES (?, ?)',
              (url, channel_id))
    conn.commit()
    conn.close()

def remove_tracker(url, channel_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('DELETE FROM event_trackers WHERE url = ? AND channel_id = ?',
              (url, channel_id))
    conn.commit()
    conn.close()

def get_all_trackers():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT url, channel_id FROM event_trackers')
    trackers = c.fetchall()
    conn.close()
    return trackers

def remove_processed_events(channel_id):
    """Remove all processed events for a specific channel"""
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('DELETE FROM processed_events WHERE channel_id = ?', (channel_id,))
    conn.commit()
    conn.close()