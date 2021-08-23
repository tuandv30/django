from django.conf.urls import url
from django.urls import include
from .statistic.urls import urlpatterns as statistic_urls
from .sorting_plan.urls import urlpatterns as sorting_plan_urls
from .operation_config.urls import urlpatterns as operation_config_urls
from . import views

urlpatterns = [
    url(r'^index$', views.index, name="crossbelt-index"),
    url(r'^statistic/', include(statistic_urls)),
    url(r'^sorting_plan/', include(sorting_plan_urls)),
    url(r'^operation_config/', include(operation_config_urls)),
]
