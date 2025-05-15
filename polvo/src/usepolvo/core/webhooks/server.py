# core/webhooks/server.py
import asyncio
import logging
from typing import Callable, Dict, Optional

from aiohttp import web
from pyngrok import ngrok

logger = logging.getLogger(__name__)


class WebhookServer:
    """
    A standalone server component for receiving and processing webhooks.
    This can be used independently or as part of the BaseWebhook implementation.
    """

    def __init__(self):
        """Initialize a new webhook server."""
        self._app = None
        self._runner = None
        self._site = None
        self._ngrok_tunnel = None
        self._handlers: Dict[str, Callable] = {}
        self._is_running = False

    def add_handler(self, path: str, handler: Callable):
        """
        Add a request handler for a specific path.

        Args:
            path: URL path to handle
            handler: Async function that processes the request
        """
        self._handlers[path] = handler
        # Update routes if server is already running
        if self._app:
            self._app.router.add_post(path, handler)

    async def start(
        self, port: int = 8080, host: str = "localhost", use_ngrok: bool = False
    ) -> str:
        """
        Start the webhook server.

        Args:
            port: Port to listen on
            host: Host to bind to
            use_ngrok: Whether to create an ngrok tunnel

        Returns:
            The base URL for the webhook server
        """
        if self._is_running:
            logger.warning("Server is already running")
            if self._ngrok_tunnel and use_ngrok:
                return self._ngrok_tunnel.public_url
            return f"http://{host}:{port}"

        # Create aiohttp application
        self._app = web.Application()

        # Add registered handlers
        for path, handler in self._handlers.items():
            self._app.router.add_post(path, handler)

        # Set up and start the server
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, host, port)
        await self._site.start()
        self._is_running = True

        base_url = f"http://{host}:{port}"

        if use_ngrok:
            try:
                self._ngrok_tunnel = ngrok.connect(port)
                logger.info(f"Ngrok tunnel established: {self._ngrok_tunnel.public_url}")
                return self._ngrok_tunnel.public_url
            except Exception as e:
                logger.error(f"Failed to create ngrok tunnel: {e}")
                logger.info(f"Falling back to local URL: {base_url}")
                return base_url

        logger.info(f"Webhook server started at {base_url}")
        return base_url

    async def stop(self):
        """Stop the webhook server and clean up resources."""
        if not self._is_running:
            logger.warning("Server is not running")
            return

        # Disconnect ngrok tunnel if it exists
        if self._ngrok_tunnel:
            try:
                ngrok.disconnect(self._ngrok_tunnel.public_url)
                logger.info("Ngrok tunnel disconnected")
            except Exception as e:
                logger.error(f"Failed to disconnect ngrok tunnel: {e}")

            try:
                ngrok.kill()
                logger.info("Ngrok process terminated")
            except Exception as e:
                logger.error(f"Failed to kill ngrok process: {e}")

        # Stop the HTTP server
        if self._site:
            await self._site.stop()
            logger.info("HTTP server stopped")

        # Clean up the runner
        if self._runner:
            await self._runner.cleanup()
            logger.info("Runner cleaned up")

        self._is_running = False
        logger.info("Webhook server fully stopped")

    @property
    def is_running(self) -> bool:
        """Check if the server is currently running."""
        return self._is_running

    @property
    def app(self) -> Optional[web.Application]:
        """Get the aiohttp application instance."""
        return self._app

    @property
    def ngrok_url(self) -> Optional[str]:
        """Get the ngrok public URL if available."""
        if self._ngrok_tunnel:
            return self._ngrok_tunnel.public_url
        return None

    async def run_forever(self):
        """Run the server indefinitely until interrupted."""
        if not self._is_running:
            raise RuntimeError("Server is not running. Call start() first.")

        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Received cancellation signal")
            await self.stop()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            await self.stop()
        except Exception as e:
            logger.error(f"Error in webhook server: {e}")
            await self.stop()
            raise


# Example usage
async def example():
    server = WebhookServer()

    async def handle_webhook(request):
        data = await request.text()
        print(f"Received webhook: {data}")
        return web.Response(text="OK")

    server.add_handler("/webhook", handle_webhook)
    url = await server.start(use_ngrok=True)
    print(f"Webhook URL: {url}/webhook")

    try:
        await server.run_forever()
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example())
