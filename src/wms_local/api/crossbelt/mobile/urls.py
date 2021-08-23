from django.conf.urls import url
from django.urls import include

from .chute import urls as chute_urlpatterns
from .printer import urls as printer_urlpatterns

urlpatterns = [
    url(r'^chute/', include(chute_urlpatterns)),
    url(r'^printer/', include(printer_urlpatterns)),
]
