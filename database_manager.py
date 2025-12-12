import sqlite3
import json
import os
from dotenv import load_dotenv
from secure_storage import encrypt_data, decrypt_data

load_dotenv()
ENCRYPTION_PASSWORD = os.getenv("ENCRYPTION_PASSWORD")

def init_db():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()

    # Create accounts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            site TEXT,
            email TEXT,
            password TEXT,
            username TEXT,
            profile TEXT,
            status TEXT
        )
    ''')

    # Create logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            site TEXT,
            action TEXT,
            timestamp REAL,
            success INTEGER,
            profile TEXT,
            value REAL
        )
    ''')

    # Create sites table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            signup_path TEXT,
            login_path TEXT,
            tasks_path TEXT,
            withdraw_path TEXT,
            min_payout REAL,
            status TEXT
        )
    ''')

    # Create persona_answers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS persona_answers (
            id INTEGER PRIMARY KEY,
            account_id INTEGER,
            question TEXT,
            answer TEXT,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
    ''')

    # Create parameters table
    c.execute('''
        CREATE TABLE IF NOT EXISTS parameters (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    conn.close()

def save_accounts(accounts):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("DELETE FROM accounts")
    for acc in accounts:
        encrypted_password = encrypt_data(acc['password'].encode(), ENCRYPTION_PASSWORD)
        c.execute("INSERT INTO accounts (site, email, password, username, profile, status) VALUES (?, ?, ?, ?, ?, ?)",
                  (acc['site'], acc['email'], encrypted_password, acc['username'], json.dumps(acc['profile']), acc['status']))
    conn.commit()
    conn.close()

def load_accounts():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT id, site, email, password, username, profile, status FROM accounts")
    accounts = []
    for row in c.fetchall():
        decrypted_password = decrypt_data(row[3], ENCRYPTION_PASSWORD).decode()
        accounts.append({
            "id": row[0],
            "site": row[1],
            "email": row[2],
            "password": decrypted_password,
            "username": row[4],
            "profile": json.loads(row[5]),
            "status": row[6]
        })
    conn.close()
    return accounts

def write_log_db(log_entry):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs (site, action, timestamp, success, profile, value) VALUES (?, ?, ?, ?, ?, ?)",
              (log_entry['site'], log_entry['action'], log_entry['timestamp'], log_entry['success'], json.dumps(log_entry['profile']), log_entry.get('value', 0)))
    conn.commit()
    conn.close()

def load_sites():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT name, signup_path, login_path, tasks_path, withdraw_path, min_payout, status FROM sites")
    sites = {}
    for row in c.fetchall():
        sites[row[0]] = {
            "signup": row[1],
            "login": row[2],
            "tasks": row[3],
            "withdraw": row[4],
            "min": row[5],
            "status": row[6]
        }
    conn.close()
    # If sites table is empty, load from sites.json
    if not sites:
        with open('sites.json') as f:
            sites_data = json.load(f)
            save_sites(sites_data)
            return sites_data
    return sites

def save_sites(sites):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    for name, data in sites.items():
        c.execute("INSERT OR REPLACE INTO sites (name, signup_path, login_path, tasks_path, withdraw_path, min_payout, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (name, data['signup'], data['login'], data['tasks'], data['withdraw'], data['min'], data.get('status', 'enabled')))
    conn.commit()
    conn.close()

def save_persona_answer(account_id, question, answer):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO persona_answers (account_id, question, answer) VALUES (?, ?, ?)",
              (account_id, question, answer))
    conn.commit()
    conn.close()

def get_persona_answer(account_id, question):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT answer FROM persona_answers WHERE account_id = ? AND question = ?", (account_id, question))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_logs():
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT site, action, timestamp, success, profile, value FROM logs")
    logs = []
    for row in c.fetchall():
        logs.append({
            "site": row[0],
            "action": row[1],
            "timestamp": row[2],
            "success": row[3],
            "profile": json.loads(row[4]),
            "value": row[5]
        })
    conn.close()
    return logs

def get_parameter(key, default=None):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("SELECT value FROM parameters WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else default

def set_parameter(key, value):
    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO parameters (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit()
    conn.close()
