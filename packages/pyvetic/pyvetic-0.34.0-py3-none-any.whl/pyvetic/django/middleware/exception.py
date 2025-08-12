from django.http import JsonResponse

from pyvetic.logger import get_logger

logger = get_logger(__name__)


class ExceptionHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.exception(f"Exception in request: {request.method} {request.path} - {exception}")
        return JsonResponse({"status": False, "message": "Internal Server Error"}, status=500)
