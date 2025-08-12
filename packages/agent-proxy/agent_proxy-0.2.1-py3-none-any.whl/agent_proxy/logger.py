# placeholder, will move content next
"""
Logging module for HTTP proxy requests and responses.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional


class ProxyLogger:
    """Handles logging of requests and responses with configurable output formats."""

    def __init__(
        self,
        log_file: Optional[str] = None,
        log_level: str = "INFO",
        log_format: str = "json",
        console_output: bool = True,
    ):
        self.log_file = log_file or "logs/proxy_requests.log"
        self.log_format = log_format
        self.console_output = console_output

        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configure logging
        self.logger = logging.getLogger("http_proxy")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler if enabled
        if console_output:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def log_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        request_id: str = None,
    ):
        """Log incoming request."""
        if self.log_format == "json":
            log_entry = {
                "type": "request",
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": body,
                "size": len(body) if body else 0,
            }
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.info(
                f"REQUEST [{request_id}] {method} {url} - Headers: {len(headers)} - Body: {len(body) if body else 0} bytes"
            )

    def log_response(
        self,
        request_id: str,
        status_code: int,
        headers: Dict[str, str],
        body: Optional[str] = None,
    ):
        """Log outgoing response."""
        if self.log_format == "json":
            log_entry = {
                "type": "response",
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "status_code": status_code,
                "headers": dict(headers),
                "body": body,
                "size": len(body) if body else 0,
            }
            self.logger.info(json.dumps(log_entry))
        else:
            self.logger.info(
                f"RESPONSE [{request_id}] {status_code} - Headers: {len(headers)} - Body: {len(body) if body else 0} bytes"
            )

    def log_error(self, request_id: str, error: str):
        """Log error."""
        if self.log_format == "json":
            log_entry = {
                "type": "error",
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(error),
            }
            self.logger.error(json.dumps(log_entry))
        else:
            self.logger.error(f"ERROR [{request_id}] {error}")

    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about the log file."""
        if not os.path.exists(self.log_file):
            return {"requests": 0, "responses": 0, "errors": 0, "file_size": 0}

        stats = {"requests": 0, "responses": 0, "errors": 0, "file_size": 0}
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if '"type": "request"' in line:
                        stats["requests"] += 1
                    elif '"type": "response"' in line:
                        stats["responses"] += 1
                    elif '"type": "error"' in line:
                        stats["errors"] += 1

            stats["file_size"] = os.path.getsize(self.log_file)
        except Exception:
            pass

        return stats