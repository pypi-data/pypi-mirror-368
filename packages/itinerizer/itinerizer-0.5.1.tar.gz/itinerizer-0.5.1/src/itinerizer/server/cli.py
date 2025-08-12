"""
CLI for running the Itinerizer FastAPI server.
"""

import sys
import argparse
import uvicorn

from ..__version__ import __version__


def main():
    """Main entry point for the server CLI."""
    parser = argparse.ArgumentParser(
        prog="itinerizer-server",
        description="Run the Itinerizer REST API server"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--storage-path",
        type=str,
        help="Custom storage path for itineraries"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Logging level (default: info)"
    )
    
    args = parser.parse_args()
    
    # Create app with custom storage path if provided
    if args.storage_path:
        from .app import create_app
        app = create_app(storage_path=args.storage_path)
        app_str = "itinerizer.server.cli:app"
    else:
        app_str = "itinerizer.server.app:app"
    
    print(f"Starting Itinerizer API server v{__version__}")
    print(f"Listening on http://{args.host}:{args.port}")
    print(f"API docs: http://{args.host}:{args.port}/api/docs")
    print("Press CTRL+C to stop")
    
    try:
        uvicorn.run(
            app_str if not args.storage_path else app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


# Global app variable for custom storage path
app = None


if __name__ == "__main__":
    sys.exit(main())