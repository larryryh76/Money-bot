import sqlite3

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.create_connection()
        self.create_tables()

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        except sqlite3.Error as e:
            print(e)

    def create_tables(self):
        try:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    site TEXT NOT NULL,
                    status TEXT DEFAULT 'new'
                );
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                );
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    name TEXT,
                    address TEXT,
                    birthdate TEXT,
                    sex TEXT,
                    mail TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                );
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS persona_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    question TEXT,
                    answer TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                );
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def add_account(self, email, password, site):
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO accounts (email, password, site) VALUES (?, ?, ?)", (email, password, site))
            self.conn.commit()
            return c.lastrowid
        except sqlite3.Error as e:
            print(e)
            return None

    def get_account(self, site):
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM accounts WHERE site = ? ORDER BY RANDOM() LIMIT 1", (site,))
            return c.fetchone()
        except sqlite3.Error as e:
            print(e)
            return None

    def update_account_status(self, account_id, status):
        try:
            c = self.conn.cursor()
            c.execute("UPDATE accounts SET status = ? WHERE id = ?", (status, account_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def add_log(self, account_id, message):
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO logs (account_id, message) VALUES (?, ?)", (account_id, message))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def add_persona(self, persona):
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO personas (account_id, name, address, birthdate, sex, mail) VALUES (?, ?, ?, ?, ?, ?)",
                      (persona['account_id'], persona['name'], persona['address'], persona['birthdate'], persona['sex'], persona['mail']))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def get_persona(self, account_id):
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM personas WHERE account_id = ?", (account_id,))
            return c.fetchone()
        except sqlite3.Error as e:
            print(e)
            return None

    def add_persona_answer(self, account_id, question, answer):
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO persona_answers (account_id, question, answer) VALUES (?, ?, ?)",
                      (account_id, question, answer))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def get_persona_answer(self, account_id, question):
        try:
            c = self.conn.cursor()
            c.execute("SELECT answer FROM persona_answers WHERE account_id = ? AND question = ?", (account_id, question))
            return c.fetchone()
        except sqlite3.Error as e:
            print(e)
            return None
