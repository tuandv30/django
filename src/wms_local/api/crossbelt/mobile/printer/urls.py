from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^GetPrinter$', views.get_printer, name='get-printer'),
    url(r'^ForwardPrinter$', views.forward_printer, name='forward-printer'),
]
