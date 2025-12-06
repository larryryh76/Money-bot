from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import os

def get_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data, password):
    salt = os.urandom(16)
    key = get_key(password, salt)
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(data).encode())
    return salt + encrypted_data

def decrypt_data(encrypted_data_with_salt, password):
    salt = encrypted_data_with_salt[:16]
    encrypted_data = encrypted_data_with_salt[16:]
    key = get_key(password, salt)
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())

def save_accounts_encrypted(accounts, password):
    encrypted_data = encrypt_data(accounts, password)
    with open("accounts.json.encrypted", "wb") as f:
        f.write(encrypted_data)

def load_accounts_encrypted(password):
    try:
        with open("accounts.json.encrypted", "rb") as f:
            encrypted_data_with_salt = f.read()
        return decrypt_data(encrypted_data_with_salt, password)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
