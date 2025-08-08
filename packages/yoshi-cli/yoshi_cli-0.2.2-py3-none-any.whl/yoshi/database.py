"""
This module provides a basic interface for connecting to and interacting with a SQLite database.
It includes functions for creating connections, executing queries, and retrieving results.
"""

import sqlite3
import sys
import os

VAULT_DECRYPTED = "vault.sqlite"
VAULT_ENCRYPTED = "vault.sqlite.aes"


def create_table() -> None:
    """Create the accounts table within the vault database."""
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS accounts (uuid text, application text,
            username text, password text, url text) """
    )
    db_connection.commit()
    db_connection.close()


def check_table() -> bool:
    """Check if the 'accounts' table exists within the vault database."""
    check = False
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(
        """ SELECT count(name) FROM sqlite_master WHERE type='table'
            AND name='accounts' """
    )
    if cursor.fetchone()[0] != 1:
        user_choice = input(
            "Password vault does not exist. Would you like to create it now? (y/n): "
        )
        if user_choice.lower() == "y":
            create_table()
            check = True
        else:
            sys.exit("Program aborted upon user request.")
    else:
        check = True
    db_connection.commit()
    db_connection.close()
    return check


def add_account(
    uuid: str, application: str, username: str, password: str, url: str
) -> None:
    """Add a new account within the vault database."""
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(
        """ INSERT INTO accounts VALUES (:uuid,:application,:username,
            :password,:url) """,
        {
            "uuid": uuid,
            "application": application,
            "username": username,
            "password": password,
            "url": url,
        },
    )
    db_connection.commit()
    db_connection.close()


def delete_account(uuid: str) -> None:
    """Delete an account within the vault database by its unique ID."""
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(""" DELETE FROM accounts WHERE uuid = :uuid """, {"uuid": uuid})
    db_connection.commit()
    db_connection.close()


def find_account(uuid: str) -> list:
    """Find an account within the vault database by its unique ID."""
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(""" SELECT * FROM accounts WHERE uuid = :uuid """, {"uuid": uuid})
    account = cursor.fetchall()
    db_connection.close()
    return account


def find_accounts() -> list:
    """Return all accounts stored within the vault database."""
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(""" SELECT * FROM accounts """)
    accounts = cursor.fetchall()
    db_connection.close()
    return accounts


def update_account(field_name: str, new_value: str, uuid: str) -> None:
    """Update an account within the vault database by its unique ID."""
    queries = {
        "application": "UPDATE accounts SET application = :new_value WHERE uuid = :uuid",
        "username": "UPDATE accounts SET username = :new_value WHERE uuid = :uuid",
        "password": "UPDATE accounts SET password = :new_value WHERE uuid = :uuid",
        "url": "UPDATE accounts SET url = :new_value WHERE uuid = :uuid",
    }
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(queries[field_name], {"new_value": new_value, "uuid": uuid})
    db_connection.commit()
    db_connection.close()


def purge_table() -> None:
    """Purge the 'accounts' table within the vault database."""
    db_connection = sqlite3.connect(VAULT_DECRYPTED)
    cursor = db_connection.cursor()
    cursor.execute(""" DROP TABLE accounts """)
    db_connection.commit()
    db_connection.close()


def purge_database() -> None:
    """Purge the entire vault database."""
    os.remove(VAULT_DECRYPTED)
