import logging
from dataclasses import dataclass

from starlette.applications import ASGIApp
from starlette.types import Receive, Scope, Send


@dataclass
class CustomExceptionHandlingMiddleware:
    """
    Middleware to log exceptions to structured logs.

    Args:
        app: The ASGI application to wrap.
        logger: The structured logger to use.
    """

    app: ASGIApp
    logger: logging.LoggerAdapter

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return None
        try:
            await self.app(scope, receive, send)
        except Exception:
            self.logger.error("an exception occurred", exc_info=True)
            await send(
                {
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [(b"content-type", b"text/plain")],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"An unexpected error occurred. Please try again later.",
                    "more_body": False,
                }
            )
