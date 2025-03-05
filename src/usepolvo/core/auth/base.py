# core/auth/base.py
from typing import Dict


class BaseAuth:
    """
    Base authentication class that provides a foundation for different auth methods.
    Specific authentication implementations (API key, OAuth2, etc) should extend this class.
    """

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        Must be implemented by child classes.

        Returns:
            Dict[str, str]: Authentication headers for requests

        Raises:
            AuthenticationError: If authentication credentials are not available
        """
        raise NotImplementedError("Subclasses must implement get_auth_headers()")

    def validate_credentials(self) -> bool:
        """
        Validate that required authentication credentials are available.
        Can be overridden by child classes that need validation.

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        return True
