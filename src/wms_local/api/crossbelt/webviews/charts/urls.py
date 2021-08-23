from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^inbound_rate$', views.chart_inbound_rate, name='crossblet-chart-inboundrate'),
    url(r'^scanner_rate$', views.chart_scanner_rate, name='crossblet-chart-scannerrate'),
    url(r'^total$', views.total_quantity, name='crossblet-chart-total'),
    url(r'^power$', views.power, name='crossblet-chart-power'),
    url(r'^imexport$', views.imexport, name='crossblet-chart-imexport'),
]
