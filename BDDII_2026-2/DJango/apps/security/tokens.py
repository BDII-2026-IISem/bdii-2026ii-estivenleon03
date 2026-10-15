import hashlib
import secrets

def generate_refresh_value():
    return secrets.token_urlsafe(48)

def hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
