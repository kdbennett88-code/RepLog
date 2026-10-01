from datetime import datetime
import sqlite3
import os

#This is my DB schema and is needed to define how my db will work on the lower level.
#That way when i need to post, list post or replies, it will be more organized and less
# code written in the long run.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'replog.db')


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
    print(title)
    print(content)
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

def get_post(post_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM posts WHERE id = ?", (post_id, ))
    row = cur.fetchone()
    conn.close()
    return row

def delete_reply(reply_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM replies WHERE id = ?", (reply_id, ))
    conn.commit()
    conn.close()
