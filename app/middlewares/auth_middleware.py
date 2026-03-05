import jwt
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, Response, status, HTTPException
from fastapi.routing import APIRoute

from app.config import settings


class AuthMiddleware:
    def __init__(self, app: Callable):
        self.app = app

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        path = request.url.path
        if path.startswith("/docs") or path.startswith("/openapi.json"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
            )

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        exp = datetime.fromtimestamp(payload.get("exp", 0), timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

        request.state.user = payload
        return await call_next(request)


def add_auth_middleware(app) -> None:
    app.middleware("http")(AuthMiddleware(app))
    for route in app.routes:
        if isinstance(route, APIRoute):
            original_endpoint = route.endpoint

            async def endpoint_wrapper(
                request: Request,
                *args,
                **kwargs,
            ):
                return await original_endpoint(request, *args, **kwargs)

            route.endpoint = endpoint_wrapper