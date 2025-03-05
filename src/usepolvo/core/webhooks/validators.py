# arms/webhooks/validators.py
import hashlib
import hmac
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Type, Union

logger = logging.getLogger(__name__)


class SignatureValidator(ABC):
    """
    Abstract base class for signature verification strategies.
    Developers should subclass this to implement their own verification logic.
    """

    @classmethod
    @abstractmethod
    def verify(cls, payload: Union[str, bytes], signature: str, secret_key: str, **kwargs) -> bool:
        """
        Verify a webhook signature.

        Args:
            payload: Raw request body as string or bytes
            signature: The signature from webhook header
            secret_key: The webhook secret key
            **kwargs: Additional verification parameters

        Returns:
            True if signature is valid, False otherwise

        Raises:
            ValueError: If verification fails
        """
        pass


class HmacSha256Validator(SignatureValidator):
    """
    Standard HMAC-SHA256 signature verification.
    Provided as a reference implementation and for common use cases.
    """

    @classmethod
    def verify(cls, payload: Union[str, bytes], signature: str, secret_key: str, **kwargs) -> bool:
        # Ensure we're working with strings
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        # Strip quotes if present
        signature = signature.strip('"')
        secret_key = secret_key.strip('"')

        # Compute HMAC
        computed_signature = hmac.new(
            key=secret_key.encode("utf-8"), msg=payload.encode("utf-8"), digestmod=hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison
        return hmac.compare_digest(computed_signature, signature)


# Registry of verifiers
_VERIFIERS: Dict[str, Type[SignatureValidator]] = {
    "hmac_sha256": HmacSha256Validator,
}


def register_verifier(name: str, verifier_class: Type[SignatureValidator]):
    """
    Register a new signature verifier.

    Args:
        name: Name of the verifier to register
        verifier_class: SignatureValidator subclass to register

    Example:
        ```python
        class GithubValidator(SignatureValidator):
            @classmethod
            def verify(cls, payload, signature, secret_key, **kwargs):
                # GitHub-specific verification logic
                return verified

        register_verifier("github", GithubValidator)
        ```
    """
    if not issubclass(verifier_class, SignatureValidator):
        raise TypeError("Validator must be a subclass of SignatureValidator")
    _VERIFIERS[name] = verifier_class
    logger.info(f"Registered verifier: {name}")


def get_verifier(name: str) -> Type[SignatureValidator]:
    """
    Get a verifier by name.

    Args:
        name: Name of the verifier to get

    Returns:
        The verifier class

    Raises:
        ValueError: If no verifier with the given name is registered
    """
    if name not in _VERIFIERS:
        raise ValueError(f"No verifier registered with name: {name}")
    return _VERIFIERS[name]


def list_verifiers() -> List[str]:
    """
    Get a list of all registered verifiers.

    Returns:
        List of verifier names
    """
    return list(_VERIFIERS.keys())


def verify_signature(
    payload: Union[str, bytes],
    signature: str,
    secret_key: str,
    signature_type: str = "hmac_sha256",
    **kwargs,
) -> bool:
    """
    Verify a webhook signature.

    Args:
        payload: Raw request body as string or bytes
        signature: The signature from webhook header
        secret_key: The webhook secret key
        signature_type: Type of signature verification to use
        **kwargs: Additional verification parameters

    Returns:
        True if signature is valid

    Raises:
        ValueError: If verification fails or if signature_type is not registered
    """
    # Get the appropriate verifier
    verifier = get_verifier(signature_type)

    # Perform verification
    return verifier.verify(payload, signature, secret_key, **kwargs)


def verify_hmac_signature(payload: Union[str, bytes], signature: str, secret_key: str):
    """
    Verify webhook signature using HMAC-SHA256 (for backward compatibility).

    Args:
        payload: Raw request body as string or bytes
        signature: The signature from webhook header
        secret_key: The webhook secret key

    Raises:
        ValueError: If signature verification fails
    """
    if not verify_signature(payload, signature, secret_key, "hmac_sha256"):
        raise ValueError("Invalid webhook signature")


def is_valid_signature(
    payload: Union[str, bytes],
    signature: str,
    secret_key: str,
    signature_type: str = "hmac_sha256",
    **kwargs,
) -> bool:
    """
    Check if a webhook signature is valid without raising exceptions.

    Args:
        payload: Raw request body as string or bytes
        signature: The signature from webhook header
        secret_key: The webhook secret key
        signature_type: Type of signature verification to use
        **kwargs: Additional verification parameters

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        return verify_signature(payload, signature, secret_key, signature_type, **kwargs)
    except ValueError as e:
        logger.warning(f"Signature verification failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during signature verification: {e}")
        return False


# Example of how to implement a custom verifier
"""
# Example: Implementing a GitHub webhook verifier

class GithubValidator(SignatureValidator):
    @classmethod
    def verify(cls, payload, signature, secret_key, **kwargs):
        # Ensure we're working with strings
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        # GitHub prefixes the signature with 'sha256='
        if not signature.startswith("sha256="):
            raise ValueError("Invalid GitHub signature format")

        # Strip the prefix
        signature = signature.replace("sha256=", "")

        # Compute the HMAC
        computed_signature = hmac.new(
            key=secret_key.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison
        return hmac.compare_digest(computed_signature, signature)

# Register the verifier
register_verifier("github", GithubValidator)

# Use the verifier
is_valid = verify_signature(payload, signature, secret_key, "github")
"""
