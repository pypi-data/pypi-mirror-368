"""
REST Tester - A GUI application for testing REST APIs with server and client functionality.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("rest-tester")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development/uninstalled package
    __version__ = "0.1.0-dev"

__author__ = "David Kracht"
__email__ = "david.kracht@mail.de"

# Make the package executable
def main():
    """Entry point for the package."""
    from .main import main as app_main
    app_main()
