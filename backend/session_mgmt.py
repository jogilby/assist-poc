import secrets
from datetime import datetime, timedelta, timezone
import sqlite3

SESSION_EXPIRY_MINUTES = 60

# Function to create a new session
def create_user_session(user_id: str, provider: str, access_token: str):
    session_id = secrets.token_urlsafe(32)  # Secure session ID
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=SESSION_EXPIRY_MINUTES)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (session_id, user_id, provider, access_token, expiration) VALUES (?, ?, ?, ?, ?)",
                   (session_id, user_id, provider, access_token, expires_at))
    conn.commit()
    conn.close()
    
    return session_id

def get_session(session_id: str):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, user_id, provider, access_token, expiration FROM sessions WHERE session_id = ?", (session_id,))
    return cursor.fetchone()

def delete_session(session_id: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
