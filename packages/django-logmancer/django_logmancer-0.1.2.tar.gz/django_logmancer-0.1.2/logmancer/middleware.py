import contextvars
import json
import logging
import threading
import traceback

from logmancer.conf import get_bool, should_exclude_path
from logmancer.models import LogEntry
from logmancer.utils import LogEvent, make_json_safe, mask_sensitive_data

logger = logging.getLogger("logmancer.middleware")

# Sync (thread local) and async (contextvar) storage
_thread_user = threading.local()
_context_user = contextvars.ContextVar("current_user", default=None)


class DBLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sync context
        _thread_user.user = getattr(request, "user", None)

        # Async context
        _context_user.set(getattr(request, "user", None))

        response = self.get_response(request)
        self.log_request(request, response)

        _thread_user.user = None
        _context_user.set(None)

        return response

    async def __acall__(self, request):
        # Async context
        _thread_user.user = getattr(request, "user", None)
        _context_user.set(getattr(request, "user", None))

        response = await self.get_response(request)
        self.log_request(request, response)

        _thread_user.user = None
        _context_user.set(None)

        return response

    def get_user_from_request(self, request):
        if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
            return request.user
        return None

    def log_request(self, request, response):
        if should_exclude_path(request.path):
            return
        try:
            user = self.get_user_from_request(request)

            try:
                if request.content_type == "application/json":
                    body_data = json.loads(request.body.decode("utf-8"))
                else:
                    body_data = request.POST.dict()
            except Exception:
                body_data = {}

            meta = make_json_safe(
                {
                    "GET": mask_sensitive_data(request.GET.dict()),
                    "POST": mask_sensitive_data(body_data),
                    "headers": mask_sensitive_data(
                        {k: v for k, v in request.headers.items() if k.lower() != "authorization"}
                    ),
                    "remote_addr": request.META.get("REMOTE_ADDR"),
                }
            )

            LogEntry.objects.create(
                level="INFO",
                message=f"{request.method} {request.path} - {response.status_code}",
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                user=user,
                meta=meta,
                source="middleware",
                actor_type="user" if user else "system",
            )
        except Exception:
            logger.exception("[Logmancer] Middleware log error")

    def process_exception(self, request, exception):
        if not get_bool("AUTO_LOG_EXCEPTIONS"):
            return

        try:
            user = self.get_user_from_request(request)

            meta = {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "stack": traceback.format_exc(),
            }

            LogEvent.error(
                message=f"Unhandled exception on {request.method} {request.path}",
                path=request.path,
                method=request.method,
                status_code=500,
                user=user,
                meta=meta,
                source="exception",
                actor_type="user" if user else "system",
            )
        except Exception:
            logger.exception("[Logmancer] process_exception failed")


def get_current_user():
    # Check async context
    user = _context_user.get(None)
    if user is not None:
        return user

    # Then check sync thread local
    return getattr(_thread_user, "user", None)
