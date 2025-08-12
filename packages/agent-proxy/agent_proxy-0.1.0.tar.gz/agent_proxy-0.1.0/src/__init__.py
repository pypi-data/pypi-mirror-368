"""
agent-proxy: A lightweight HTTP proxy for capturing and logging Claude CLI API requests
"""

__version__ = "1.0.0"
__author__ = "glitchee"
__email__ = "yangyuxuanf1dt@gmail.com"

from .proxy import SimpleProxy
from .logger import ProxyLogger

__all__ = ["SimpleProxy", "ProxyLogger"]