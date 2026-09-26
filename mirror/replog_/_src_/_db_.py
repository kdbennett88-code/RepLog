import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'replog.db')
# this is going to create the db and place the replog.db file inside the dir
# that I declare it to with the os functions
def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL, 
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(post_id) REFERENCES posts(id)

        )
                """)
    conn.commit()
    conn.close()

def create_post(title, content):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",(title, content))
    conn.commit()
    conn.close()

def list_posts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM posts")
    rows = cur.fetchall()
    conn.close()
    return rows

def create_reply(post_id, content):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO replies (post_id, content) VALUES (?, ?)", (post_id, content))
    conn.commit()
    conn.close()

def list_replies(post_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, post_id, content, created_at FROM replies WHERE post_id = ?", (post_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

