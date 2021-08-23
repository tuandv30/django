from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hourinduction$', views.induction_per_hour, name="crossbelt-statistic-hour-induction"),
    url(r'^induction$', views.induction, name="crossbelt-statistic-induction"),
    url(r'^imexport$', views.import_export, name="crossbelt-statistic-imexport"),
    url(r'^chute$', views.statistic_chute, name="crossbelt-statistic-chute")
]
