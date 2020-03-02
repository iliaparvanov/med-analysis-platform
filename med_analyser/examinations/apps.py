from django.apps import AppConfig
from django.conf import settings
from fastai.vision import load_learner
from pathlib import Path
import os

# from fastai.vision import *

class ExaminationsConfig(AppConfig):
    name = 'examinations'
    path = Path(os.path.join(settings.ML_MODELS))
    path_image_type = path/'image_type_model'
    path_chest_xray = path/'chest_xray_model'

    learner_image_type = load_learner(path_image_type)
    learners_findings = {
        "chest": {
            'any_findings': load_learner(path_chest_xray, 'any_findings.pkl'),
            'findings': load_learner(path_chest_xray, 'findings.pkl')
        }
    }

    def ready(self):
        from .ml_models import trainer
    
        confirmed_findings_model = self.get_model('ConfirmedFinding')
        image_type_model = self.get_model('ImageType')
        examinations_model = self.get_model('Examination')
        trainer.start(self.learners_findings, confirmed_findings_model, image_type_model, examinations_model)