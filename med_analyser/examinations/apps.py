from django.apps import AppConfig
from django.conf import settings
from fastai.vision import load_learner
from pathlib import Path
import os

# from fastai.vision import *

class ExaminationsConfig(AppConfig):
    name = 'examinations'
    path = Path(os.path.join(settings.MODELS))
    path_image_type = path/'image_type_model'
    path_chest_xray = path/'chest_xray_model'

    learner_image_type = load_learner(path_image_type)
    learner_chest_xray = load_learner(path_chest_xray)