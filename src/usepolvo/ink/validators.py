# ink/validators.py

import hashlib
import hmac


def verify_hmac_signature(payload: str, signature: str, secret_key: str):
    """
    Verify webhook signature using HMAC-SHA256.

    Args:
        payload: Raw request body as string
        signature: The signature from webhook header
        secret_key: The webhook secret key

    Raises:
        ValueError: If signature verification fails
    """
    # Strip quotes if present
    signature = signature.strip('"')
    secret_key = secret_key.strip('"')

    # Compute HMAC
    computed_signature = hmac.new(
        key=secret_key.encode("utf-8"), msg=payload.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison
    if not hmac.compare_digest(computed_signature, signature):
        raise ValueError("Invalid webhook signature")
