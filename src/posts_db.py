import os
import sqlite3
from datetime import datetime
from . import db

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "replog.db")


def get_conn():
    return sqlite3.connect(DB_PATH)

def create_post(title, content):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
            "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, dateime.utcnow().isoformat())
            )
    conn.commit()
    conn.close()

def list_posts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM posts ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "content": r[2], "created_at": r[3]} for r in rows]
    
def get_post(post_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM posts WHERE id = ?", (post_id, ))
    row = cur.fetchone()
    conn.close()
    return row

def create_reply(post_id, content):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
            "INSERT INTO replies (post_id, content, created_at) VALUES (?, ?, ?)",
            (post_id, content, datetime.utcnow().isoformat())
            )
    conn.commit()
    conn.close()

def list_replies(post_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, content, created_at FROM replies WHERE post_id = ? ORDER BY created_at ASC", (post_id, ))
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "content": r[1], "created_at": r[2]} for r in rows]

def delete_reply(reply_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM replies WHERE id = ?", (reply_id, ))
    conn.commit()
    conn.close()

