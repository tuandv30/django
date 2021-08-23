from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'chuteFull$', views.get_chute_full, name='screen-chutefull'),
    url(r'chuteDetails$', views.get_chute_details, name='screen-chutedetails'),
]
