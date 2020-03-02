from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    name = 'subscriptions'

    def ready(self):
        from . import updater
        from common.models import Hospital
        updater.start(Hospital, self.get_model('Plan'))
