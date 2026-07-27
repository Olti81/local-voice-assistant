import sqlite3
import os

DB_PATH = "history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mode TEXT,
            window_title TEXT,
            text_snippet TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_activity(mode, window_title, text_snippet):
    snippet = text_snippet[:100] + "..." if len(text_snippet) > 100 else text_snippet
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_log (mode, window_title, text_snippet) VALUES (?, ?, ?)",
        (mode, window_title, snippet)
    )
    conn.commit()
    conn.close()