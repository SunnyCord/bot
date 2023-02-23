from __future__ import annotations

from cryptography.fernet import Fernet


def check_aes() -> bytes:
    """Gets an AES key to use for encryption or generates a new one."""
    try:
        with open("keys/key.aes", "rb") as keyfile:
            key = keyfile.read()
    except FileNotFoundError:
        with open("keys/key.aes", "wb") as keyfile:
            key = Fernet.generate_key()
            keyfile.write(key)
    return key


def encode_discord_id(discord_id: int, model: Fernet) -> str:
    """Encodes data with the app key."""
    discord_id_str = str(discord_id)
    secret = model.encrypt(discord_id_str.encode())
    return str(secret.decode())
