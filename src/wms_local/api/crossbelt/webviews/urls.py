from django.conf.urls import url
from django.urls import include
from .statistic.urls import urlpatterns as statistic_url
from .charts.urls import urlpatterns as charts_url
from .sorting_plan.urls import urlpatterns as sorting_plan_urls

urlpatterns = [
    url(r'^statistic/', include(statistic_url)),
    url(r'^charts/', include(charts_url)),
    url(r'^sorting_plan/', include(sorting_plan_urls)),
]
