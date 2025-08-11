#!/usr/bin/env python3
"""
Main entry point for the REST Tester application.
"""

import sys
import os
import argparse
import signal
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import importlib.resources

def get_config_path():
    """
    Get the path to the config file with the following priority:
    1. resources/config.yaml in current working directory (user config)
    2. config.yaml in current working directory (user config)
    3. Default config from the installed package (creates temp copy)
    """
    # First, check if there's a user config (local config) development (default config)
    local_config = "resources/config.yaml"
    if os.path.exists(local_config):
        print(f"Using local (development) config (assumed to be next default config, if released): {os.path.abspath(local_config)}")
        return local_config

    # Second, check if there's a user config in the current directory
    local_config = "config.yaml"
    if os.path.exists(local_config):
        print(f"Using local config (custom config): {os.path.abspath(local_config)}")
        return local_config

    # If no local config, use the resource from the package
    try:
        # Use importlib.resources to access the config.yaml from the installed package
        resources_ref = importlib.resources.files('rest_tester') / 'resources' / 'config.yaml'
        
        if resources_ref.is_file():
            # Use as_file context manager to get a file path that ConfigModel can use
            # Note: We need to keep the file available for the entire application lifetime
            global _temp_config_file
            _temp_config_file = importlib.resources.as_file(resources_ref)
            temp_path = _temp_config_file.__enter__()
            print(f"Using resource config (automatically deployed): {temp_path}")
            return str(temp_path)
        else:
            raise FileNotFoundError("Resource config.yaml not found in package")
            
    except Exception as e:
        raise FileNotFoundError(f"Failed to load resource config: {e}")

# Global variable to keep the context manager alive
_temp_config_file = None

def parse_arguments():
    """Parse command line arguments."""
    from . import __version__
    
    parser = argparse.ArgumentParser(
        description="REST Tester - Test Application für REST APIs (Server and Client)",
        prog="rest-tester"
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    return parser.parse_args()

def setup_signal_handling(app, window):
    """Setup signal handling for graceful shutdown with Ctrl+C."""
    def signal_handler(signum, frame):
        print("\nShutting down gracefully...")
        # Force close the window first
        if window:
            window.close()
        # Then quit the application
        app.quit()
    
    # Set up signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create a timer to allow Python to process signals
    # This is necessary because Qt's event loop blocks signal processing
    timer = QTimer(app)  # Parent the timer to the app
    timer.start(100)  # Check for signals every 100ms (more responsive)
    timer.timeout.connect(lambda: None)  # Dummy slot to keep the timer running
    
    return timer  # Return timer to keep it alive

def main():
    """Main application entry point."""
    # Parse command line arguments (this will handle --version automatically)
    parse_arguments()
    
    try:
        from .gui_model import ConfigModel
        from .instances_gui import MainWindow
        
        app = QApplication(sys.argv)
        
        # Get config path (will create default if none exists)
        config_path = get_config_path()
        config = ConfigModel(config_path)
        
        # Create and show main window
        window = MainWindow(config)
        window.resize(1600, 900)
        window.show()
        
        # Setup signal handling for Ctrl+C (after window is created)
        timer = setup_signal_handling(app, window)
        
        # Run application
        exit_code = app.exec()
        
        # Clean up temporary config file if it was created
        global _temp_config_file
        if _temp_config_file is not None:
            _temp_config_file.__exit__(None, None, None)
            
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting REST Tester: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
