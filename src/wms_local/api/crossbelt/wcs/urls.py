from django.conf.urls import url
from django.urls import include

from .chute import urls as chute_urlpatterns
from .destination import urls as destination_urlpatterns
from .device import urls as device_urlpatterns
from .sorting_report import urls as sorting_report_urlpatterns

urlpatterns = [
    url(r'^chute/', include(chute_urlpatterns)),
    url(r'^destination/', include(destination_urlpatterns)),
    url(r'^sorting_report', include(sorting_report_urlpatterns)),
    url(r'^device/', include(device_urlpatterns)),
]
