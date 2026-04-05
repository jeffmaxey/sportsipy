"""WSGI entry point for production deployment."""
from sportsipy_dashboard.app import server as application

__all__ = ["application"]
