"""
Custom Decorators
"""

# Third Party Library
from django.shortcuts import redirect, reverse
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.http import Http404

# Local Library
from app.modules.util.helpers import Helpers
from app.modules.core.response import Response
from app.modules.entity.option_entity import Option_Entity


def redirect_if_authenticated(function):
    def wrap(controller, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            if "redirect" in request.GET:
                return redirect(request.GET["redirect"])
            return redirect("app.web.admin.dashboard")
        return function(controller, request, *args, **kwargs)
    return wrap


def login_if_not_authenticated(function):
    def wrap(controller, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return redirect(reverse("app.web.login") + "?redirect=" + request.get_full_path())
        return function(controller, request, *args, **kwargs)
    return wrap


def stop_request_if_authenticated(function):
    def wrap(controller, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            response = Response()
            return JsonResponse(response.send_private_failure([{
                "type": "error",
                "message": _("Error! Access forbidden for authenticated users.")
            }]))
        return function(controller, request, *args, **kwargs)
    return wrap


def redirect_if_not_installed(function):
    def wrap(controller, request, *args, **kwargs):
        installed = False if Option_Entity().get_one_by_key("app_installed") is False else True
        if not installed:
            return redirect("app.web.install")
        return function(controller, request, *args, **kwargs)
    return wrap


def protect_metric_with_auth_key(function):
    def wrap(controller, request, *args, **kwargs):
        if kwargs["type"] == "prometheus":
            prometheus_token = Option_Entity().get_one_by_key("prometheus_token")
            if prometheus_token.value != "" and ("HTTP_AUTHORIZATION" not in request.META or prometheus_token.value != request.META["HTTP_AUTHORIZATION"]):
                raise Http404("Host not found.")
        return function(controller, request, *args, **kwargs)
    return wrap


def stop_request_if_installed(function):
    def wrap(controller, request, *args, **kwargs):
        installed = False if Option_Entity().get_one_by_key("app_installed") is False else True
        if installed:
            response = Response()
            return JsonResponse(response.send_private_failure([{
                "type": "error",
                "message": _("Error! Application is already installed.")
            }]))
        return function(controller, request, *args, **kwargs)
    return wrap


def log_request_data(function):
    def wrap(controller, request, *args, **kwargs):
        correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        helper = Helpers()
        logger = helper.get_logger(__name__)
        logger.debug(_("Request Method: %(method)s {'correlationId':'%(correlationId)s'}") % {
            "method": request.method,
            "correlationId": correlation_id
        })
        logger.debug(_("Request URL: %(path)s {'correlationId':'%(correlationId)s'}") % {
            "path": request.path,
            "correlationId": correlation_id
        })
        logger.debug(_("Request Body: %(body)s {'correlationId':'%(correlationId)s'}") % {
            "body": request.body,
            "correlationId": correlation_id
        })
        return function(controller, request, *args, **kwargs)
    return wrap
