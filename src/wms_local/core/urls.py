# -*- coding: utf-8 -*-
import logging

from django.conf.urls import url

from . import views

_logger = logging.getLogger(__name__)

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^403', views.handle_403, name='handle-403'),
    url(r'^404', views.handle_404, name='handle-404'),
    url(r'^500', views.handle_500, name='handle-500'),
]
