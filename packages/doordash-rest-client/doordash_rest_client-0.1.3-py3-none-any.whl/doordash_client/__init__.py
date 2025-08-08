"""
DoorDash Python Client

A simple Python client for the DoorDash API.
"""

from .client import DoorDashClient
from .exceptions import *

__version__ = "0.1.2"
__author__ = "DoorDash Automation Suite" 
__email__ = "support@example.com"

__all__ = [
    "DoorDashClient",
    "DoorDashClientError",
    "APIError", 
    "NetworkError",
    "AuthenticationError",
]