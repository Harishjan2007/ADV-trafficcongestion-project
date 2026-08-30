"""
FastAPI Compatibility Layer with Zero-Dependency Fallback
Ensures clean IDE resolution and standalone execution even before pip install.
"""

from typing import Any, Callable, Dict, List, Optional
import importlib.util


# Check dynamically if fastapi is installed
_has_fastapi = importlib.util.find_spec("fastapi") is not None

if _has_fastapi:
    _fastapi_mod = __import__("fastapi", fromlist=["FastAPI", "APIRouter", "HTTPException", "Query"])
    _cors_mod = __import__("fastapi.middleware.cors", fromlist=["CORSMiddleware"])
    FastAPI = _fastapi_mod.FastAPI
    APIRouter = _fastapi_mod.APIRouter
    HTTPException = _fastapi_mod.HTTPException
    Query = _fastapi_mod.Query
    CORSMiddleware = _cors_mod.CORSMiddleware
else:
    # Graceful standalone definitions when fastapi is not yet installed in global site-packages
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
            super().__init__(f"HTTP {status_code}: {detail}")

    def Query(default: Any = ..., **kwargs: Any) -> Any:
        return default

    class APIRouter:
        def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):
            self.prefix = prefix
            self.tags = tags or []
            self.routes: Dict[str, Any] = {}

        def get(self, path: str, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                self.routes[f"GET {self.prefix}{path}"] = func
                return func
            return decorator

        def post(self, path: str, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                self.routes[f"POST {self.prefix}{path}"] = func
                return func
            return decorator

    class CORSMiddleware:
        pass

    class FastAPI:
        def __init__(self, title: str = "", description: str = "", version: str = ""):
            self.title = title
            self.description = description
            self.version = version
            self.routes: Dict[str, Any] = {}

        def add_middleware(self, middleware_class: Any, **kwargs: Any) -> None:
            pass

        def include_router(self, router: APIRouter) -> None:
            self.routes.update(router.routes)

        def get(self, path: str, **kwargs: Any) -> Callable:
            def decorator(func: Callable) -> Callable:
                self.routes[f"GET {path}"] = func
                return func
            return decorator
