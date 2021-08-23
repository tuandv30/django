# -*- coding: utf-8 -*-
import logging

from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

_logger = logging.getLogger(__name__)


def home(_request):
    return redirect("adminsorting:index")


def handle_404(request, _exception=None):
    ctx = {
        "error_code": 404,
        "error_message": _("Page Not Found"),
        "error_description": _("Sorry, but the page you are looking for has note been found. Try checking the URL "
                               "for error, then hit the refresh button on your browser or try found something else "
                               "in our app.")
    }
    return TemplateResponse(request, 'error/base.html',
                            context=ctx, status=404)


def handle_403(request, _exception=None):
    ctx = {
        "error_code": 403,
        "error_message": _("Forbidden"),
        "error_description": _("Sorry, but the page you are looking for has note been forbidden.")
    }
    return TemplateResponse(request, 'error/base.html',
                            context=ctx, status=404)


def handle_500(request, _exception=None):
    ctx = {
        "error_code": 500,
        "error_message": _("Internal Server Error"),
        "error_description": _("The server encountered something unexpected that didn't allow it to complete "
                               "the request. We apologize.")
    }
    return TemplateResponse(request, 'error/base.html',
                            context=ctx, status=500)
