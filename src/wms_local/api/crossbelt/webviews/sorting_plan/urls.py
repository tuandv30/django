from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'get_dst$', views.get_dst, name='crossbelt-get-dst'),
    url(r'get_dst_station$', views.get_dst_station, name='crossbelt-get-dst-station'),
]
