import sqlite3
import json
import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "osint_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            scan_date TEXT NOT NULL,
            raw_data TEXT NOT NULL,
            graph_data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_scan(target: str, raw_data: dict, graph_data: dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Store timestamp as ISO format string
    now = datetime.datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO scan_history (target, scan_date, raw_data, graph_data)
        VALUES (?, ?, ?, ?)
    ''', (target, now, json.dumps(raw_data), json.dumps(graph_data)))
    
    conn.commit()
    conn.close()

def get_history():
    """Returns a list of past scans without the heavy raw data for the list view."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, target, scan_date FROM scan_history ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "target": row[1],
            "scan_date": row[2]
        })
    return history

def get_scan_by_id(scan_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT target, scan_date, raw_data, graph_data FROM scan_history WHERE id = ?', (scan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "target": row[0],
            "scan_date": row[1],
            "raw_data": json.loads(row[2]),
            "graph_data": json.loads(row[3])
        }
    return None
