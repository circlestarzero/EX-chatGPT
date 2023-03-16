import sqlite3
import threading
db_lock = threading.Lock()
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        uuid TEXT NOT NULL,
        chat_name TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    ''')

    conn.commit()
def clear_chat_lists_for_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_lists WHERE user_id = ?", (user_id,))
    conn.commit()
def insert_chat_lists(conn,user_id, chat_lists):
    with db_lock:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        for chat_list in chat_lists["chatLists"]:
            uuid = chat_list["uuid"]
            chat_name = chat_list["chatName"]
            cursor.execute(
                "INSERT INTO chat_lists (user_id, uuid, chat_name) VALUES (?, ?, ?)",
                (user_id, uuid, chat_name)
            )
        conn.commit()

def get_chat_lists_by_user_id(conn, user_id):
    cursor = conn.cursor()
    create_tables(conn)
    cursor.execute('''
        SELECT c.uuid, c.chat_name
        FROM chat_lists c
        WHERE c.user_id = ?
        ORDER BY id DESC;
    ''', (user_id,))
    res = cursor.fetchall()
    if not res:
        default_chat_lists = {
            "chatLists": [
                {
                    "uuid": "default",
                    "chatName": "Default",
                }
            ]
        }
        insert_chat_lists(conn, user_id, default_chat_lists)
        chat_lists = [{"uuid": "default", "chatName": "Default"}]
    else:
        chat_lists = [{"uuid": row[0], "chatName": row[1]} for row in res]
    return {"chatLists": chat_lists}


if __name__ == "__main__":
    conn = sqlite3.connect('chat_lists.db')

    create_tables(conn)

    user_chat_lists = get_chat_lists_by_user_id(conn, "githubID")
    print(user_chat_lists)

    conn.close()