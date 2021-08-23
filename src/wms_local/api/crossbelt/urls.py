from django.conf.urls import url
from django.urls import include

from .wcs import urls as wcs_urlpatterns
from .screen_android import urls as screen_urlpatterns
from .mobile import urls as mobile_urlpatterns
from .webviews import urls as webviews_urlpatterns

urlpatterns = [
    url(r'^wcs/', include(wcs_urlpatterns)),
    url(r'^mobile/', include(mobile_urlpatterns)),
    url(r'^android/', include(screen_urlpatterns)),
    url(r'^webviews/', include(webviews_urlpatterns)),
]
