from django.apps import AppConfig
from django.conf import settings
import os

class ExaminationsConfig(AppConfig):
    name = 'examinations'
    path = os.path.join(settings.MODELS, 'models.py')