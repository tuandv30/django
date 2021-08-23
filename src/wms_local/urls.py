from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.urls import include
from django.views.i18n import JavaScriptCatalog, set_language
from django.contrib import admin
from .account.urls import urlpatterns as account_urls
from .adminsorting.urls import urlpatterns as adminsorting_urls
from .core.urls import urlpatterns as core_urls
from .api.urls import urlpatterns as api_urls

handler404 = 'wms_local.core.views.handle_404'
handler403 = 'wms_local.core.views.handle_403'
handler500 = 'wms_local.core.views.handle_500'

non_translatable_urlpatterns = [
    url(r'^i18n/$', set_language, name='set_language'),
    url(r'^api/',
        include((api_urls, 'api'), namespace='api')),
]

translatable_urlpatterns = [
    url(r'^', include(core_urls)),
    url(r'^account/',
        include((account_urls, 'account'), namespace='account')),
    url(r'^adminsorting/',
        include((adminsorting_urls, 'adminsorting'), namespace='adminsorting')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'admin/', admin.site.urls),
]

urlpatterns = non_translatable_urlpatterns + i18n_patterns(*translatable_urlpatterns)
