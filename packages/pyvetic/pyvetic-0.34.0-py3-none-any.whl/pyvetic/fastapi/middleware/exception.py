from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from pyvetic.logger import get_logger

logger = get_logger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Return generic error response to client
            logger.exception(f"Exception in request: {request.method} {request.url.path} - {e}")
            return JSONResponse(status_code=500, content={"status": False, "message": "Internal Server Error"})
