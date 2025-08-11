import base64
import json
import os
from operator import ifloordiv

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Crypter:
    def __init__(self, key: str | bytes):
        """Initialize instance based on key as urlsafe_b64encoded string"""
        self.f = Fernet(key)

    def encrypt(self, data: str) -> bytes:
        return self.f.encrypt(data=data.encode())

    def decrypt(self, token: bytes) -> str | None:
        try:
            return self.f.decrypt(token=token).decode()
        except InvalidToken:
            print("Invalid token, most likely the key is incorrect")
            return None

    def encrypt_json(self, json_data) -> bytes:
        """Encrypt JSON to bytes."""
        json_string = json.dumps(json_data)
        return self.encrypt(data=json_string)

    def decrypt_to_json(self, token: bytes):
        """Decrypt token back to JSON"""
        decrypted = self.decrypt(token=token)
        return json.loads(decrypted) if decrypted else None

    @classmethod
    def generate_key(cls) -> bytes:
        """generate key and return it as urlsafe_b64encode encoded string"""
        return Fernet.generate_key()

    @staticmethod
    def _derive_key(salt_b: bytes, password: str) -> bytes:
        """Derive the key from the `password` using the passed `salt`

        see: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_b,
            iterations=1_200_000, )

        return kdf.derive(password.encode())

    @classmethod
    def generate_key_salt_from_password(cls, password: str, size=16) -> (str, str):
        """Generate key and salt from password and return them as base64.urlsafe_b64encode string
        """
        salt_b = os.urandom(16)  # returns bytes
        salt = cls.to_urlsafe_str(salt_b)  # convert to string
        key_b = cls._derive_key(salt_b=salt_b, password=password)
        key = cls.to_urlsafe_str(key_b)  # convert to string
        return key, salt

    @classmethod
    def from_password_salt(cls, password: str, salt: str):
        """alternative constructor to initiate instance of Crypt"""
        salt_b = cls.to_bytes(salt)  # convert to bytes
        key_b = cls._derive_key(salt_b=salt_b, password=password)
        key = cls.to_urlsafe_str(key_b)  # convert to string
        return cls(key)

    @staticmethod
    def to_urlsafe_str(raw_bytes: bytes):
        return base64.urlsafe_b64encode(raw_bytes).decode()

    @staticmethod
    def to_bytes(urlsafe_str):
        return base64.urlsafe_b64decode(urlsafe_str.encode())


if __name__ == '__main__':
    mykey, mysalt = Crypter.generate_key_salt_from_password(password="my_password")
    print(type(mykey))
    print(f"{mykey=}")
    crypter = Crypter(key=mykey)

    example_data = {"name": "Alice", "role": "admin"}

    example_token = crypter.encrypt_json(json_data=example_data)
    string_based_token = crypter.encrypt(data="A simple string for testing")
    print(f"{example_token=}")

    filename = "/Users/niko/Desktop/temp.enc"
    with open(filename, "wb") as file:
        file.write(example_token)

    # -------------

    with open(filename, "rb") as file:
        tkn = file.read()

    crypter_2 = Crypter.from_password_salt(password="my_password", salt=mysalt)

    print(f"decrypted: {crypter_2.decrypt_to_json(token=tkn)}")
    print(f"decrypted: {crypter_2.decrypt(token=string_based_token)}")
