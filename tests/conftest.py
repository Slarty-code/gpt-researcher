"""
Pytest configuration and fixtures for Dex-researcher.

Ensures the backend directory is on sys.path so imports like
`from utils import ...` in backend.server.server_utils resolve correctly
when tests import from backend.
"""
import os
import sys

# Add backend directory to path so "from utils import ..." in server_utils works
_root = os.path.dirname(os.path.abspath(__file__))
_backend = os.path.abspath(os.path.join(_root, "..", "backend"))
if _backend not in sys.path:
    sys.path.insert(0, _backend)
