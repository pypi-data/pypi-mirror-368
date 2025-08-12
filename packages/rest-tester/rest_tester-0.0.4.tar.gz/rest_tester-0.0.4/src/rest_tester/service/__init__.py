"""
Service layer for REST Tester application.
Contains server management, client management and endpoint utilities.
"""

from .rest_server_manager import RestServerManager
from .rest_client_manager import RestClientManager
from .endpoint_utils import make_generic_handler

__all__ = ['RestServerManager', 'RestClientManager', 'make_generic_handler']
