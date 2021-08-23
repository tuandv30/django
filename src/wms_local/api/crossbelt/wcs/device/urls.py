from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload$', views.upload_state, name='upload-state'),
]
