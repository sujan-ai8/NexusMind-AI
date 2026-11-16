import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response

