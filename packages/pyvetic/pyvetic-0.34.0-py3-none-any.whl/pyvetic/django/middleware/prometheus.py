import time

from django.http import HttpRequest

from pyvetic.instrument.prometheus import MetricsCollectorSingleton


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.metrics_collector = MetricsCollectorSingleton.get_instance()

    def __call__(self, request: HttpRequest):
        request._start_time = time.time()

        response = self.get_response(request)

        resolver_match = request.resolver_match
        endpoint = resolver_match.route if resolver_match and resolver_match.route else "INVALID_REQUEST"

        status_code = str(response.status_code)
        latency = time.time() - request._start_time

        self.metrics_collector.observe_request(request.method, endpoint, status_code)
        self.metrics_collector.observe_request_latency(request.method, endpoint, status_code, latency)

        return response

    def process_exception(self, request, exception):
        latency = time.time() - request._start_time

        resolver_match = request.resolver_match
        endpoint = resolver_match.route if resolver_match and resolver_match.route else "INVALID_REQUEST"

        self.metrics_collector.observe_request(request.method, endpoint, "500")
        self.metrics_collector.observe_request_latency(request.method, endpoint, "500", latency)
        self.metrics_collector.observe_exception(request.method, endpoint, "500")

        return None


# class MetricsMiddlewareV2:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.metrics_collector = MetricsCollectorSingleton.get_instance()

#     def __call__(self, request):
#         method = request.method
#         # Get the URL pattern instead of actual path
#         resolver_match = request.resolver_match
#         endpoint = resolver_match.route if resolver_match and resolver_match.route else "INVALID_REQUEST"

#         start_time = time.time()
#         status_code = "500"  # Default to 500 if exception

#         try:
#             response = self.get_response(request)
#             status_code = str(response.status_code)
#             return response

#         except Exception as e:
#             # Increment exception counter
#             self.metrics_collector.observe_exception(method, endpoint, status_code)
#             raise
#         finally:
#             # Increment request counter
#             self.metrics_collector.observe_request(method, endpoint, status_code)

#             # Record latency
#             latency = time.time() - start_time
#             self.metrics_collector.observe_request_latency(method, endpoint, status_code, latency)
