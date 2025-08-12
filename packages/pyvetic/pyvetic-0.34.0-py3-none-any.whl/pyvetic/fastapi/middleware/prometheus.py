import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Route

from pyvetic.instrument.prometheus import MetricsCollectorSingleton
from pyvetic.logger import get_logger

logger = get_logger(__name__)


def get_endpoint(request: Request):
    route: Route = request.scope.get("route")
    endpoint = route.path if route else "INVALID_REQUEST"
    return endpoint


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        metrics_collector = MetricsCollectorSingleton.get_instance()

        method = request.method

        start_time = time.time()
        status_code = "500"  # Default to 500 if exception

        try:
            response = await call_next(request)

            endpoint = get_endpoint(request)

            status_code = str(response.status_code)
            return response

        except Exception as e:
            # Increment exception counter
            endpoint = get_endpoint(request)
            metrics_collector.observe_exception(method, endpoint, status_code)
            raise
        finally:
            # Increment request counter
            metrics_collector.observe_request(method, endpoint, status_code)

            # Record latency
            latency = time.time() - start_time
            metrics_collector.observe_request_latency(method, endpoint, status_code, latency)
