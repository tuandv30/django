from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.plan_list, name='crossbelt-plan-list'),
    url(r'^create/$', views.plan_create, name='crossbelt-plan-create'),
    url(r'^(?P<plan_id>[0-9]+)/delete/$', views.plan_delete, name='crossbelt-plan-delete'),
    url(r'^(?P<plan_id>[0-9]+)/$', views.plan_details, name='crossbelt-plan-details'),
    url(r'^switch/$', views.plan_switch, name='crossbelt-plan-switch'),
    url(r'^active/$', views.plan_active, name='crossbelt-plan-active'),
]
