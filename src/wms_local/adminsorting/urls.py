from django.urls import include
from django.conf.urls import url
from . import views as core_views
from .crossbelt.urls import urlpatterns as crossbelt_dashboard_url

urlpatterns = [
    url(r'^$', core_views.index, name='index'),
    url(r'^crossbelt/', include(crossbelt_dashboard_url))
]
