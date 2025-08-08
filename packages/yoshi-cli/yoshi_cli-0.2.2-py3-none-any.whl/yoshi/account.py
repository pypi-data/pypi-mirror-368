"""
This script imports necessary modules for database interactions.

Modules imported:
    - database: A custom module providing database functionality.
"""

from yoshi import database


class Account:
    """Represents a login account."""

    def __init__(
        self,
        uuid: str,
        application: str,  # pylint: disable=R0913,R0917
        username: str,  # pylint: disable=R0913,R0917
        password: str,
        url: str,
    ) -> None:  # pylint: disable=R0913,R0917
        self.uuid = uuid
        self.application = application
        self.username = username
        self.password = password
        self.url = url

    def display_account(self) -> None:
        """Print the account details."""
        print("ID:", self.uuid)
        print("Application:", self.application)
        print("Username:", self.username)
        print("Password:", self.password)
        print("URL:", self.url)

    def save_account(self) -> None:
        """Save the account details to the database."""
        database.add_account(
            self.uuid, self.application, self.username, self.password, self.url
        )

    def delete_account(self) -> bool:
        """Delete the account from the database.

        Returns:
            bool: True if the deletion was successful.
        """
        database.delete_account(self.uuid)
        return True
