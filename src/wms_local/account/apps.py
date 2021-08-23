from __future__ import unicode_literals

from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'wms_local.account'

    def ready(self):
        pass
