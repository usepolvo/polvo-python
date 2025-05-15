# core/clients/rest.py
from typing import Any, Dict

from usepolvo.core.clients.base import BaseClient


class RESTClient(BaseClient):
    """Template for REST APIs with standard CRUD operations."""

    def list(self, resource: str, **params) -> Dict[str, Any]:
        """GET /resource/"""
        return self._request("GET", f"{resource}/", params=params)

    def get(self, resource: str, id: str) -> Dict[str, Any]:
        """GET /resource/{id}/"""
        return self._request("GET", f"{resource}/{id}/")

    def create(self, resource: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /resource/"""
        return self._request("POST", f"{resource}/", json=data)

    def update(self, resource: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT /resource/{id}/"""
        return self._request("PUT", f"{resource}/{id}/", json=data)

    def delete(self, resource: str, id: str) -> None:
        """DELETE /resource/{id}/"""
        self._request("DELETE", f"{resource}/{id}/")
