import sqlite3
from typing import Optional

class DataService:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.conn = self.connect()
        self.db_created = False  # Neues Flag
        self.create_database()

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create_database(self) -> None:
        cursor = self.conn.cursor()
        # Überprüfen Sie, ob die Tabelle bereits existiert
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processed_emails'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            # Wenn die Tabelle nicht existiert, setzen Sie das Flag und erstellen Sie die Tabelle
            self.db_created = True

        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS processed_emails (
                    account TEXT,
                    mailbox TEXT,
                    email_uid TEXT,
                    processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    PRIMARY KEY (account, mailbox, email_uid)
                )''')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_account_mailbox_uid ON processed_emails (account, mailbox, email_uid)')

    def email_processed(self, account: str, mailbox: str, email_uid: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM processed_emails WHERE account = ? AND mailbox = ? AND email_uid = ?', (account, mailbox, email_uid))
        return cursor.fetchone() is not None

    def insert_email(self, account: str, mailbox: str, email_uid: str, status: str) -> None:
        with self.conn:
            self.conn.execute('INSERT INTO processed_emails (account, mailbox, email_uid, status) VALUES (?, ?, ?, ?)', (account, mailbox, email_uid, status))

    def close(self) -> None:
        if self.conn:
            self.conn.close()
