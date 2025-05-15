# src/usepolvo/core/clients/user_context.py
from contextlib import contextmanager
from typing import Any, Dict, Optional, TypeVar

from usepolvo.core.auth.multi_user import MultiUserOAuth2Auth
from usepolvo.core.clients.base import BaseClient

T = TypeVar("T", bound="UserContextClientMixin")


class UserContextClientMixin:
    """
    Mixin for clients that support user context.
    Provides methods for setting and managing user context.
    """

    def __init__(self):
        self._current_user_id = None
        # This assumes the auth attribute will be set by the class that uses this mixin

    def for_user(self: T, user_id: str) -> T:
        """
        Set the user context for subsequent operations.

        Args:
            user_id: User ID

        Returns:
            Self for method chaining
        """
        self._current_user_id = user_id
        if hasattr(self, "auth") and isinstance(self.auth, MultiUserOAuth2Auth):
            self.auth.set_current_user(user_id)
        return self

    @contextmanager
    def user_context(self: T, user_id: str):
        """
        Context manager for user-specific operations.

        Args:
            user_id: User ID
        """
        previous_user_id = self._current_user_id
        self._current_user_id = user_id
        if hasattr(self, "auth") and isinstance(self.auth, MultiUserOAuth2Auth):
            previous_auth_user = getattr(self.auth, "_current_user_id", None)
            self.auth.set_current_user(user_id)

        try:
            yield self
        finally:
            self._current_user_id = previous_user_id
            if hasattr(self, "auth") and isinstance(self.auth, MultiUserOAuth2Auth):
                self.auth.set_current_user(previous_auth_user)

    def get_current_user_id(self) -> Optional[str]:
        """
        Get the current user ID.

        Returns:
            Current user ID or None
        """
        return self._current_user_id
