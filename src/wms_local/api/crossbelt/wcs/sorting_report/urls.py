from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.sorting_report, name='sorting-report'),
]
