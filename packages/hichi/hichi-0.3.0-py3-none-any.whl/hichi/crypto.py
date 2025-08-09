from cryptography.fernet import Fernet
import os
from .config import CONFIG_DIR

KEY_FILE = os.path.join(CONFIG_DIR, "key.key")

def generate_key():
    """Generates a new encryption key and saves it to a file."""
    key = Fernet.generate_key()
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def get_key():
    """Retrieves the encryption key, generating one if it doesn't exist."""
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt(value: str) -> bytes:
    """Encrypts a string value."""
    key = get_key()
    f = Fernet(key)
    return f.encrypt(value.encode())

def decrypt(token: bytes) -> str:
    """Decrypts an encrypted token."""
    key = get_key()
    f = Fernet(key)
    return f.decrypt(token).decode()