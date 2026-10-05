import sys
import os

# Add root directory to python path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    if scope["type"] in ("http", "websocket"):
        # Vercel rewrites might set scope['path'] to the destination ('/api/index.py').
        # Recover the original user URL path from x-matched-path header if available.
        headers = dict(scope.get("headers", []))
        matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
        if matched_path and matched_path != "/api/index.py":
            scope["path"] = matched_path
        elif scope["path"] == "/api/index.py":
            scope["path"] = "/"
    await fastapi_app(scope, receive, send)
