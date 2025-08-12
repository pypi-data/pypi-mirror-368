"""
Core proxy functionality for HTTP request interception and forwarding.
"""

import time
import uuid
from typing import Dict, Optional

import httpx
from fastapi import FastAPI, Request, Response

from .logger import ProxyLogger


class SimpleProxy:
    """Simple HTTP proxy that intercepts and logs requests."""

    def __init__(self, target_base_url: str, logger: Optional[ProxyLogger] = None):
        self.target_base_url = target_base_url.rstrip("/")
        self.logger = logger or ProxyLogger()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    def generate_request_id(self) -> str:
        """Generate unique request ID."""
        return f"req_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming HTTP request."""
        request_id = self.generate_request_id()

        # Build target URL
        path = request.url.path
        if request.url.query:
            path += f"?{request.url.query}"
        target_url = f"{self.target_base_url}{path}"

        # Read request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            body_str = body.decode("utf-8") if body else None
        else:
            body_str = None

        # Log request
        self.logger.log_request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            body=body_str,
            request_id=request_id,
        )

        try:
            # Forward request to target
            async with self.client.stream(
                method=request.method,
                url=target_url,
                headers={
                    k: v
                    for k, v in request.headers.items()
                    if k.lower() not in ["host", "content-length"]
                },
                content=body,
                params=dict(request.query_params),
            ) as response:
                # Read response content
                response_content = await response.aread()
                response_body = response_content.decode("utf-8") if response_content else None

                # Log response
                self.logger.log_response(
                    request_id=request_id,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response_body,
                )

                # Return response to client
                return Response(
                    content=response_content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

        except httpx.TimeoutException:
            self.logger.log_error(request_id, "Gateway Timeout")
            return Response(
                content="Gateway Timeout",
                status_code=504,
                headers={"Content-Type": "text/plain"},
            )
        except httpx.ConnectError as e:
            self.logger.log_error(request_id, f"Connection error: {e}")
            return Response(
                content="Bad Gateway",
                status_code=502,
                headers={"Content-Type": "text/plain"},
            )
        except Exception as e:
            self.logger.log_error(request_id, f"Unexpected error: {e}")
            return Response(
                content="Internal Server Error",
                status_code=500,
                headers={"Content-Type": "text/plain"},
            )

    def create_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(
            title="HTTP Proxy CLI",
            description="Simple HTTP proxy for intercepting and logging requests",
            version="0.1.0",
        )

        @app.api_route(
            "/{path:path}",
            methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        )
        async def proxy_all_requests(request: Request) -> Response:
            """Handle all HTTP methods and paths."""
            return await self.handle_request(request)

        @app.get("/")
        async def root():
            """Root endpoint with proxy info."""
            return {
                "message": "HTTP Proxy CLI Server",
                "target_site": self.target_base_url,
                "logs": self.logger.log_file,
                "endpoints": {"proxy": "/{any_path}", "info": "/"},
            }

        @app.get("/proxy-info")
        async def proxy_info():
            """Get proxy configuration info."""
            return {
                "target_site": self.target_base_url,
                "log_file": self.logger.log_file,
                "uptime": time.time(),
            }

        return app