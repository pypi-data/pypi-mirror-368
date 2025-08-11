import time
from typing import Tuple, Optional
import logging

from prometheus_client import (
    REGISTRY,
    CONTENT_TYPE_LATEST,
    generate_latest,
    Counter,
    Gauge,
    Histogram,
)
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

INFO = Gauge("api_app_info", "API application information.", [])
REQUESTS = Counter(
    "api_requests_total",
    "Total number of requests received by method and path.",
    ["method", "path"],
)
RESPONSES = Counter(
    "api_responses_total",
    "Total number of responses sent by method, path, and status code.",
    ["method", "path", "status_code"],
)
REQUESTS_PROCESSING_TIME = Histogram(
    "api_requests_duration_seconds",
    "Histogram of request processing time by method and path (in seconds).",
    ["method", "path"],
)
EXCEPTIONS = Counter(
    "api_exceptions_total",
    "Total number of exceptions raised by method, path, and exception type.",
    ["method", "path", "exception_type"],
)
REQUESTS_IN_PROGRESS = Gauge(
    "api_requests_in_progress",
    "Number of requests currently being processed by method and path.",
    ["method", "path"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for ASGI applications.

    Tracks request counts, response codes, exceptions, durations, and in-progress requests.

    Args:
        app: The ASGI application.
        log_exceptions: If True (default), log exceptions raised during request processing.
                        Set to False to disable middleware-level exception logging.
    """

    def __init__(self, app: ASGIApp, log_exceptions: bool = True) -> None:
        super().__init__(app)
        self.log_exceptions = log_exceptions
        INFO.inc()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path, is_instrumented = self._resolve_path(request)

        if not is_instrumented:
            return await call_next(request)

        self._inc_in_progress(method, path)
        self._inc_requests(method, path)
        start_time = time.perf_counter()
        status_code: Optional[int] = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            self._observe_duration(method, path, start_time)
        except BaseException as exc:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            self._inc_exceptions(method, path, exc)
            if self.log_exceptions:
                logger.exception("Exception in request processing")
            raise
        finally:
            self._inc_responses(method, path, status_code)
            self._dec_in_progress(method, path)

        return response

    @staticmethod
    def _resolve_path(request: Request) -> Tuple[str, bool]:
        """
        Returns the matched route path and whether it is instrumented.
        """
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True
        return request.url.path, False

    @staticmethod
    def _inc_requests(method: str, path: str) -> None:
        """Increment the requests counter for the given method and path."""
        REQUESTS.labels(method=method, path=path).inc()

    @staticmethod
    def _inc_responses(method: str, path: str, status_code: int) -> None:
        """Increment the responses counter for the given method, path, and status code."""
        RESPONSES.labels(method=method, path=path, status_code=status_code).inc()

    @staticmethod
    def _observe_duration(method: str, path: str, start_time: float) -> None:
        """Observe the duration of a request for the given method and path."""
        duration = time.perf_counter() - start_time
        REQUESTS_PROCESSING_TIME.labels(method=method, path=path).observe(duration)

    @staticmethod
    def _inc_exceptions(method: str, path: str, exc: BaseException) -> None:
        """Increment the exceptions counter for the given method, path, and exception type."""
        EXCEPTIONS.labels(
            method=method, path=path, exception_type=type(exc).__name__
        ).inc()

    @staticmethod
    def _inc_in_progress(method: str, path: str) -> None:
        """Increment the in-progress requests gauge for the given method and path."""
        REQUESTS_IN_PROGRESS.labels(method=method, path=path).inc()

    @staticmethod
    def _dec_in_progress(method: str, path: str) -> None:
        """Decrement the in-progress requests gauge for the given method and path."""
        REQUESTS_IN_PROGRESS.labels(method=method, path=path).dec()


def metrics(request: Request) -> Response:
    """ASGI endpoint to expose Prometheus metrics."""
    return Response(
        generate_latest(REGISTRY),
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )
