"""
Password Vault Manager

This script provides various functions for managing password vaults.
It allows users to create, list, edit and delete accounts.

The `Account` class represents an individual account, with attributes for
the application name, username, password, and URL. The database module is used
to interact with the SQLite database file (`vault.sqlite`) that stores the
accounts data.

Functions:
    generate_characters(n): generates a list of random characters
    shuffle_characters(characters): shuffles the characters to create a password
    generate_passphrase(n, sep): generates an XKCD-style passphrase with n words and separator
    list_accounts(): lists all saved accounts in the database
    delete_account(uuid): deletes an account by its UUID
    purge_accounts(): purges the entire database (irreversible)
    create_account(): creates a new account by prompting user for details
    edit_account(uuid, edit_parameter): edits an existing account's details

Usage:
    Run this script in your terminal to access these functions.
"""

from string import ascii_letters, punctuation, digits
import random
import secrets
import uuid
from prettytable import PrettyTable
from yoshi.account import Account
from yoshi import database
from yoshi.wordlist import WORDLIST


def generate_characters(n: int) -> list:
    """
    Generates a list of n random characters from the set of ASCII letters,
    punctuation and digits.

    Args:
        n (int): The number of characters to generate

    Returns:
        list: A list of n random characters
    """
    characters = []
    password_format = ascii_letters + punctuation + digits
    for _ in range(n):
        characters.append(secrets.choice(password_format))
    return characters


def shuffle_characters(characters: list) -> str:
    """
    Shuffles the characters to create a password.

    Args:
        characters (list): The list of characters

    Returns:
        str: A string representation of the shuffled characters
    """
    random.shuffle(characters)
    character_string = "".join(characters)
    return character_string


def generate_passphrase(n: int, sep: str) -> str:
    """
    Generates an XKCD-style passphrase with n words and separator.

    Args:
        n (int): The number of words to include
        sep (str): The separator symbol

    Returns:
        str: A string representation of the passphrase
    """
    phrases = []
    lucky_number = secrets.choice(range(0, n))
    for _ in range(n):
        word = secrets.choice(WORDLIST)
        if _ == lucky_number:
            phrases.append(word.capitalize() + str(_))
        else:
            phrases.append(word.capitalize())
    passphrase = sep.join(phrases)
    return passphrase


def list_accounts() -> None:
    """
    Lists all saved accounts in the database.

    Returns:
        None
    """
    accounts = database.find_accounts()
    t = PrettyTable(["UUID", "Application", "Username", "Password", "URL"])
    for account in accounts:
        t.add_row([account[0], account[1], account[2], account[3], account[4]])
    print(t)


def delete_account(account_uuid: str) -> None:
    """
    Deletes an account by its UUID.

    Args:
        account_uuid (str): The UUID of the account to delete

    Returns:
        None
    """
    account_record = database.find_account(account_uuid)
    account = Account(
        account_record[0][0],
        account_record[0][1],
        account_record[0][2],
        account_record[0][3],
        account_record[0][4],
    )
    if account.delete_account():
        print("Account successfully deleted.")


def purge_accounts() -> None:
    """
    Purges the entire database (irreversible).

    Returns:
        None
    """
    check = input(
        """Are you absolutely sure you want to delete your password vault?
        This action is irreversible. (y/n): """
    )
    if check.lower() == "y":
        database.purge_table()
        database.purge_database()
        print(
            "The password vault has been purged. You may now exit or create a new one."
        )


def create_account() -> None:
    """
    Creates a new account by prompting user for details.

    Returns:
        None
    """
    application_string = input("Please enter a name for this account: ")
    username_string = input("Please enter your username for this account: ")
    url_string = input("(Optional) Please enter a URL for this account: ")

    password_type = input(
        """Do you want a random character password (p), an XKCD-style passphrase
(x), or a custom password (c)? (p|x|c): """
    )
    if password_type not in ["p", "x", "c"]:
        print("Error: Invalid choice. Please choose p, x, or c.")
        return

    if password_type == "x":
        password_length = int(
            input("Please enter number of words to include (min. 2): ")
        )
        if password_length < 3:
            print("Error: Your passphrase length must be at least 3 words.")
            return
        password_separator = input(
            "Please enter your desired separator symbol (_,-, ~, etc.): "
        )
        password_string = generate_passphrase(password_length, password_separator)
    elif password_type == "p":
        password_length = int(
            input("Please enter your desired password length (min. 8): ")
        )
        if password_length < 8:
            print("Error: Your password length must be at least 8 characters.")
            return
        password_characters = generate_characters(password_length)
        password_string = shuffle_characters(password_characters)
    else:
        password_string = input("Please enter your desired password: ")

    account = Account(
        str(uuid.uuid4()),
        application_string,
        username_string,
        password_string,
        url_string,
    )
    account.save_account()
    print("Account saved to the vault. Use `--list` to see all saved accounts.")


def edit_account(account_uuid: str, edit_parameter: int) -> None:
    """
    Allow users to edit any account information except the UUID.

    Args:
        account_uuid (str): Unique identifier of the account.
        edit_parameter (int): Parameter indicating which field to edit.
            Valid values are 1 for application name, 2 for username,
            3 for password, and 4 for URL.
    """
    field_name, new_value = ""
    if edit_parameter == 1:
        field_name = "application"
        new_value = input("Please enter your desired Application name: ")
    elif edit_parameter == 2:
        field_name = "username"
        new_value = input("Please enter your desired username: ")
    elif edit_parameter == 3:
        field_name = "password"
        type_check = input(
            "Do you want a new random password or to enter a custom password? "
            "(random/custom): "
        ).lower()
        if type_check == "random":
            password_length = int(input("Please enter your desired password length: "))
            if password_length < 8:
                print("Error: Your password length must be at least 8 characters.")
            else:
                password_characters = generate_characters(password_length)
                new_value = shuffle_characters(password_characters)
        else:
            new_value = input("Please enter your desired password: ")
    elif edit_parameter == 4:
        field_name = "url"
        new_value = input("Please enter your desired URL: ")
    database.update_account(field_name, new_value, account_uuid)
    print("Account successfully updated.")
