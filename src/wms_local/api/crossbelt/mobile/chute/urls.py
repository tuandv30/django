from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^GetChutev2$', views.get_chute_v2, name='get-chute-v2'),
    url(r'^GetPackagev2$', views.get_package_v2, name='get-package-v2'),
    url(r'^CleanPackage$', views.clean_package, name='clean-package'),
    url(r'^CleanPackageChute$', views.clean_package_chute, name='clean-package-chute'),
]
