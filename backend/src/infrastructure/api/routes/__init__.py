"""
API Routes

FastAPI route modules for different endpoints.
"""
from . import auth_routes, client_routes, chart_routes

__all__ = [
    "auth_routes",
    "client_routes",
    "chart_routes",
]
