import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.logging import logger
from src.core.metrics import HTTP_REQUEST_DURATION_SECONDS


class MetricsAndLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            status_code = str(response.status_code)

            if not path.endswith("/metrics"):
                HTTP_REQUEST_DURATION_SECONDS.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).observe(duration)
                logger.info(
                    f"[HTTP] {method} {path} - Status: {status_code} - Duration: {duration * 1000:.2f}ms"
                )

            return response
        except Exception as exc:
            duration = time.perf_counter() - start_time
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=path,
                status_code="500"
            ).observe(duration)
            logger.error(
                f"[HTTP_ERROR] {method} {path} failed with {exc.__class__.__name__}: {exc}"
            )
            raise
