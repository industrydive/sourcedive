from __future__ import unicode_literals

from django.apps import AppConfig


class SourcesConfig(AppConfig):
    name = 'sources'
    verbose_name = 'Source Database'

    def ready(self):
        Person = self.get_model('Person')
