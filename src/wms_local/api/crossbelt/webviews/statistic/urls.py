from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^induction$', views.statistic_induction, name='crossbelt-statistic-induction'),
    url(r'^chute$', views.statistic_chute, name='crossbelt-statistic-chute'),
]
