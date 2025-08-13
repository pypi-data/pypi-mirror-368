import sys
import argparse

from pacificpy.core.app import PacificApp
from pacificpy.core.server import run
from pacificpy.core.settings import Settings


def main():
    parser = argparse.ArgumentParser(description="PacificPy CLI")
    parser.add_argument("--host", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    parser.add_argument("--no-uvloop", action="store_true", help="Disable uvloop")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--env-file", help="Path to .env file")
    
    args = parser.parse_args()
    
    # Create settings
    settings = Settings.from_env(args.env_file)
    
    # Override settings with command line arguments if provided
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port
    
    # Create a simple app for testing
    app = PacificApp()
    
    # Run the app
    run(
        app, 
        host=settings.host, 
        port=settings.port, 
        use_uvloop=not args.no_uvloop, 
        reload=args.reload or settings.debug
    )


if __name__ == "__main__":
    main()