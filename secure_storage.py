from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
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
    encrypted_data = f.encrypt(data)
    return salt + encrypted_data

def decrypt_data(encrypted_data_with_salt, password):
    salt = encrypted_data_with_salt[:16]
    encrypted_data = encrypted_data_with_salt[16:]
    key = get_key(password, salt)
    f = Fernet(key)
    return f.decrypt(encrypted_data)
