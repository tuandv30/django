from django.conf.urls import url
from django.urls import include

from .ping import urls as ping_urlpatterns
from .crossbelt import urls as crossbelt_urlpatterns

urlpatterns = [
    url(r'^ping/', include(ping_urlpatterns)),
    url(r'^crossbelt/', include(crossbelt_urlpatterns)),
]
