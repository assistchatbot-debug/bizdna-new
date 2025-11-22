def verify_webhook_secret(secret: str, token: str) -> bool:
    return secret == token
