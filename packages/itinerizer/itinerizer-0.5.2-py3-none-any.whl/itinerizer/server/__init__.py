"""
Itinerizer FastAPI server module.

Optional REST API server for Itinerizer.
"""

from .app import create_app, get_app

__all__ = ["create_app", "get_app"]