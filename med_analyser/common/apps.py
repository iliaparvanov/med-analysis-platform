from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'common'

    def ready(self):
        from . import updater
        hospitals_model = self.get_model('Hospital')
        updater.start(hospitals_model)