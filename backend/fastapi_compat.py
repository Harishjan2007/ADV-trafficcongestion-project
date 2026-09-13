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


try:
    from fastapi.testclient import TestClient
except Exception:
    import urllib.parse
    import inspect

    class TestResponse:
        def __init__(self, status_code: int, data: Any):
            self.status_code = status_code
            self._data = data

        def json(self):
            if hasattr(self._data, "model_dump"):
                return self._data.model_dump()
            if hasattr(self._data, "dict"):
                return self._data.dict()
            if isinstance(self._data, list):
                return [x.model_dump() if hasattr(x, "model_dump") else (x.dict() if hasattr(x, "dict") else x) for x in self._data]
            return self._data

        @property
        def text(self):
            import json
            try:
                return json.dumps(self.json())
            except Exception:
                return str(self._data)

    class TestClient:
        def __init__(self, app: Any):
            self.app = app

        def get(self, url: str, **kwargs) -> TestResponse:
            parsed = urllib.parse.urlparse(url)
            path = parsed.path
            query_params = urllib.parse.parse_qs(parsed.query)
            params = {k: v[0] for k, v in query_params.items()}

            route_key = f"GET {path}"
            handler = None

            if isinstance(self.app.routes, dict):
                handler = self.app.routes.get(route_key)
                if not handler:
                    # Check for path parameter matching, e.g. /api/cities/{city_id}
                    for rk, fn in self.app.routes.items():
                        if rk.startswith("GET ") and "{" in rk:
                            template = rk[4:]
                            parts_t = template.strip("/").split("/")
                            parts_p = path.strip("/").split("/")
                            if len(parts_t) == len(parts_p):
                                matched = True
                                path_args = {}
                                for pt, pp in zip(parts_t, parts_p):
                                    if pt.startswith("{") and pt.endswith("}"):
                                        path_args[pt[1:-1]] = pp
                                    elif pt != pp:
                                        matched = False
                                        break
                                if matched:
                                    handler = fn
                                    params.update(path_args)
                                    break
            elif isinstance(self.app.routes, list):
                def _flatten_routes(route_list):
                    flat = []
                    for r in route_list:
                        if hasattr(r, "original_router") and hasattr(r.original_router, "routes"):
                            flat.extend(_flatten_routes(r.original_router.routes))
                        elif hasattr(r, "routes"):
                            flat.extend(_flatten_routes(r.routes))
                        else:
                            flat.append(r)
                    return flat

                for route in _flatten_routes(self.app.routes):
                    if hasattr(route, "methods") and "GET" in route.methods:
                        r_path = getattr(route, "path", "")
                        if r_path == path:
                            handler = getattr(route, "endpoint", None)
                            break
                        if "{" in r_path:
                            parts_t = r_path.strip("/").split("/")
                            parts_p = path.strip("/").split("/")
                            if len(parts_t) == len(parts_p):
                                matched = True
                                path_args = {}
                                for pt, pp in zip(parts_t, parts_p):
                                    if pt.startswith("{") and pt.endswith("}"):
                                        path_args[pt[1:-1]] = pp
                                    elif pt != pp:
                                        matched = False
                                        break
                                if matched:
                                    handler = getattr(route, "endpoint", None)
                                    params.update(path_args)
                                    break

            if handler:
                try:
                    sig = inspect.signature(handler)
                    call_args = {}
                    for param_name, param in sig.parameters.items():
                        if param_name in params:
                            val = params[param_name]
                            if param.annotation is int:
                                val = int(val)
                            call_args[param_name] = val
                        elif param.default is not inspect.Parameter.empty:
                            def_val = param.default
                            if hasattr(def_val, "default"):
                                def_val = def_val.default if def_val.default is not ... else None
                            if def_val is not None:
                                call_args[param_name] = def_val
                    res = handler(**call_args)
                    return TestResponse(200, res)
                except Exception as e:
                    return TestResponse(500, {"error": str(e)})

            return TestResponse(404, {"detail": "Not Found"})
