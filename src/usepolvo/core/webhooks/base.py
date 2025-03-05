# core/webhooks/base.py
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union

from aiohttp import web

from usepolvo.core.webhooks.server import WebhookServer
from usepolvo.core.webhooks.validators import is_valid_signature

logger = logging.getLogger(__name__)


class BaseWebhook(ABC):
    """
    Base class for all webhook handlers in Polvo.
    Provides core functionality for receiving, verifying, and processing webhooks.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        signature_header: Optional[str] = None,
        signature_type: str = "hmac_sha256",
    ):
        """
        Initialize a webhook handler.

        Args:
            secret_key: Optional secret key for signature verification
            signature_header: HTTP header name containing the signature
            signature_type: Type of signature verification to use
        """
        self.handlers: Dict[str, Callable] = {}
        self.secret_key = secret_key
        self.signature_header = signature_header
        self.signature_type = signature_type
        self.server = WebhookServer()
        self._webhook_path = None

    def set_secret_key(self, key: str):
        """Set the secret key for signature verification."""
        self.secret_key = key

    def register(self, event_type: str, handler: Optional[Callable] = None):
        """
        Register a handler for a specific event type.
        Can be used as a decorator or direct method.

        Args:
            event_type: The type of event to register for
            handler: The handler function (can be None when used as decorator)
        """
        if handler is None:
            return lambda h: self.register(event_type, h)
        self.handlers[event_type] = handler
        return handler

    async def process(self, payload: Any, signature: Optional[str] = None) -> Any:
        """
        Process an incoming webhook payload.

        Args:
            payload: The webhook payload
            signature: Optional signature for verification

        Returns:
            The result of the handler
        """
        # Verify signature if provided
        if signature and self.secret_key:
            self.verify_signature(
                payload if isinstance(payload, (str, bytes)) else json.dumps(payload), signature
            )

        event_type = self.get_event_type(payload)
        handler = self.handlers.get(event_type, self.default_handler)
        return await handler(payload)

    def verify_signature(self, payload: Union[str, bytes], signature: str, **kwargs):
        """
        Verify the webhook signature.

        Args:
            payload: Raw request body as string or bytes
            signature: The signature from the header
            **kwargs: Additional arguments for specific verifiers

        Raises:
            ValueError: If signature verification fails
        """
        if not is_valid_signature(
            payload, signature, self.secret_key, self.signature_type, **kwargs
        ):
            raise ValueError(f"Invalid webhook signature using {self.signature_type} verification")

    @abstractmethod
    def get_event_type(self, payload: Any) -> str:
        """
        Extract the event type from the payload.
        Must be implemented by subclasses.

        Args:
            payload: The webhook payload

        Returns:
            The event type as a string
        """
        pass

    @abstractmethod
    async def default_handler(self, payload: Any) -> Any:
        """
        Default handler for unhandled webhook events.
        Must be implemented by subclasses.

        Args:
            payload: The webhook payload

        Returns:
            Any response from processing
        """
        pass

    async def _handle_webhook(self, request: web.Request) -> web.Response:
        """
        Handle incoming webhook request.

        Args:
            request: The incoming HTTP request

        Returns:
            HTTP response
        """
        logger.info(f"Received webhook request to {request.path}")

        # Get raw request body
        raw_body = await request.text()

        # Get signature
        signature = request.headers.get(self.signature_header)

        # Get additional verification parameters from headers if needed
        verification_params = {}
        if self.signature_type == "slack":
            verification_params["timestamp"] = request.headers.get("X-Slack-Request-Timestamp", "0")

        try:
            if self.secret_key and signature:
                # Verify signature using raw body
                self.verify_signature(raw_body, signature, **verification_params)
                logger.info("Webhook signature verified successfully")

            # Parse JSON after verification
            try:
                payload = json.loads(raw_body)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON payload, using raw text")
                payload = raw_body

            # Process webhook
            logger.info(f"Processing webhook with event type: {self.get_event_type(payload)}")
            result = await self.process(payload)

            return web.json_response({"status": "success", "result": result})

        except ValueError as e:
            logger.error(f"Webhook validation error: {str(e)}")
            return web.Response(status=400, text=str(e))
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return web.Response(status=500, text=str(e))

    async def start_server(self, path: str, port: int = 8080, use_ngrok: bool = True) -> str:
        """
        Start the webhook server.

        Args:
            path: URL path to listen on
            port: Port to listen on
            use_ngrok: Whether to create an ngrok tunnel

        Returns:
            The public URL to use for webhooks
        """
        self._webhook_path = path
        self.server.add_handler(path, self._handle_webhook)

        base_url = await self.server.start(port=port, use_ngrok=use_ngrok)
        webhook_url = f"{base_url}{path}"

        logger.info(f"Webhook server started. URL: {webhook_url}")
        return webhook_url

    async def stop_server(self):
        """Stop the webhook server and clean up resources."""
        await self.server.stop()
        logger.info("Webhook server stopped")

    async def run(self, path: str, port: int = 8080, use_ngrok: bool = True):
        """
        Run the webhook server until interrupted.

        Args:
            path: URL path to listen on
            port: Port to listen on
            use_ngrok: Whether to create an ngrok tunnel
        """
        webhook_url = await self.start_server(path, port, use_ngrok)
        logger.info(f"Use this URL in your webhook settings: {webhook_url}")

        try:
            await self.server.run_forever()
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            logger.info("Received cancellation, shutting down...")
        finally:
            await self.stop_server()
