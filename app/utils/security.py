import base64
from cryptography.fernet import Fernet, InvalidToken
import pyotp


class EncryptionService:
    def __init__(self, secret_key: str | None = None):
        key = (secret_key or 'fallback-key').encode()
        key = base64.urlsafe_b64encode(key.ljust(32, b'0')[:32])
        self._fernet = Fernet(key)

    def encrypt_sensitive_data(self, data: str) -> str:
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_data.encode()).decode()
        except InvalidToken:
            return ''


class MFAService:
    def generate_totp_secret(self):
        return pyotp.random_base32()

    def verify_totp_token(self, secret: str, token: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

    def generate_current_token(self, secret: str) -> str:
        return pyotp.TOTP(secret).now()
