from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.config_list, name='crossbelt-operation-config-list'),
]
