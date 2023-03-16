import sqlite3
import json
from datetime import datetime
import threading
import os
from sqlite3 import Error
# Create a global lock
db_lock = threading.Lock()
program_path = os.path.realpath(__file__)
program_dir = os.path.dirname(program_path)
user_db_name = "users.db"
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(program_dir+'/'+user_db_name)
    except Error as e:
        print(e)
    return conn
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        convo_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_time TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    ''')

    conn.commit()

def insert_user_history(conn, user_id, user_history_data):
    with db_lock:
        cursor = conn.cursor()

        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        for history_item in user_history_data:
            convo_id = history_item["convo_id"]
            role = history_item["role"]
            content = history_item["content"]
            created_time = history_item["time"]
            cursor.execute(
                "INSERT INTO user_history (user_id, convo_id, role, content, created_time) VALUES (?, ?, ?, ?, ?)",
                (user_id, convo_id, role, content, created_time)
            )
        conn.commit()

def get_all_user_history(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.user_id, h.convo_id, h.role, h.content, h.created_time
        FROM users u
        JOIN user_history h ON u.user_id = h.user_id
        WHERE u.user_id = ?
        ORDER BY h.created_time DESC;
    ''', (user_id,))
    history = {}
    for row in cursor.fetchall():
        convo_id = row[1]
        history_item = {"role": row[2], "content": row[3]}
        if convo_id not in history:
            history[convo_id] = []
        history[convo_id].append(history_item)
    return {
        "user_id": user_id,
        "history": history
    }

def get_user_recent_history(conn, user_id, convo_id, limit):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.user_id, h.convo_id, h.role, h.content, h.created_time
        FROM users u
        JOIN user_history h ON u.user_id = h.user_id
        WHERE u.user_id = ? AND h.convo_id = ?
        ORDER BY h.id
        LIMIT ?;
    ''', (user_id, convo_id, limit))
    
    history = []
    for row in cursor.fetchall():
        history_item = {"role": row[2], "content": row[3]}
        history.append(history_item)
    return history

if __name__ == "__main__":
    # Connect to the database (or create a new one)
    conn = create_connection()

    # Create tables
    create_tables(conn)

    # JSON data to insert
    user_history = {
        "user_id": "123456789",
        "history": {
            "default": [
                {"role": "user", "content": "something"},
                {"role": "user", "content": "something_else"},
            ],
            "xxx": [
                {"role": "user", "content": "something"},
                {"role": "user", "content": "something_else"},
            ],
        },
    }

    # Insert JSON data
    # insert_user_history(conn, user_history)

    # Get recent history
    # recent_history = get_recent_history(conn, "123456789")
    # print(json.dumps(recent_history, indent=2))

    # Close the connection
    if conn:
        conn.close()
