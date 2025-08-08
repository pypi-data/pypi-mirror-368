"""
This module imports the Fernet symmetric encryption algorithm from the cryptography library.

It allows for secure encryption and decryption of data using a secret key.
"""

from cryptography.fernet import Fernet

VAULT_FILE = "vault.sqlite"


def generate_key() -> bytes:
    """Generates a new encryption key."""
    return Fernet.generate_key()


def load_key(key_file: str) -> bytes:
    """
    Loads an existing encryption key from the file.

    Args:
        key_file (str): Path to the key file.
    """
    with open(key_file, "rb") as key:
        return key.read()


def encrypt(key: bytes, filename: str = VAULT_FILE) -> None:
    """Encrypts the data in the specified file using the provided key."""
    f = Fernet(key)
    with open(filename, "rb") as vault:
        data = vault.read()
    encrypted_data = f.encrypt(data)
    with open(filename, "wb") as vault:
        vault.write(encrypted_data)


def decrypt(key: bytes, filename: str = VAULT_FILE) -> None:
    """Decrypts the data in the specified file using the provided key."""
    f = Fernet(key)
    with open(filename, "rb") as vault:
        encrypted_data = vault.read()
    decrypted_data = f.decrypt(encrypted_data)
    with open(filename, "wb") as vault:
        vault.write(decrypted_data)
