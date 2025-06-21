from urllib.parse import urlparse, urljoin
from flask import request
from cryptography.fernet import Fernet

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
    ref_url.netloc == test_url.netloc

class TokenEncryptor:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    # Only needed to generate the key once
    def generate_key():
        return Fernet.generate_key()

    def encrypt(self, token):
        return self.fernet.encrypt(token)
    
    def decrypt(self, encrypted_token):
        return self.fernet.decrypt(encrypted_token)
        