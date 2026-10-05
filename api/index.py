import sys
import os

# Add root directory to python path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = {k.decode("utf-8", errors="ignore").lower(): v.decode("utf-8", errors="ignore") for k, v in scope.get("headers", [])}
        path = scope.get("path", "")
        
        # Check potential Vercel routing headers
        matched = (
            headers.get("x-matched-path")
            or headers.get("x-forwarded-uri")
            or headers.get("x-vercel-matched-path")
            or ""
        )
        
        # If the path arrived as the handler script, recover the client's actual path
        if path in ("/api/index.py", "/api/index", "/api", "/api/"):
            if matched and matched not in ("/api/index.py", "/api/index", "/api", "/api/"):
                scope["path"] = matched.split("?")[0]
            else:
                scope["path"] = "/"
        elif matched and not path.startswith("/api/"):
            scope["path"] = matched.split("?")[0]
            
    await fastapi_app(scope, receive, send)
