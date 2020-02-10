from django.db import models
from common.models import Doctor
from django.urls import reverse
from django.conf import settings
import uuid
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver

from pathlib import Path
from fastai.vision.image import open_image 
from .apps import ExaminationsConfig

class Examination(models.Model):
    EXAMINATION_TYPES = [
        ('chest', 'Chest X-Ray'),
        ('elbow', 'Elbow X-Ray'),
        ('finger', 'Finger X-Ray'),
        ('forearm', 'Forearm X-Ray'),
        ('hand', 'Hand X-Ray'),
        ('humerus', 'Humerus X-Ray'),
        ('shoulder', 'Shoulder X-Ray'),
        ('wrist', 'Wrist X-Ray'),
        ('not labeled', 'Not labeled')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pat_name = models.CharField(verbose_name='name of patient', max_length=100)
    image = models.ImageField(upload_to='examination_images/', blank=True)
    notes = models.TextField()
    examination_type = models.CharField(max_length=15, choices=EXAMINATION_TYPES, default='not labeled')
    created_by = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='examinations')
    created_on = models.DateField(verbose_name='examination creation date')

    def __str__(self):
        return 'Examination ' + str(self.id) + ' for patient ' + self.pat_name

    def get_absolute_url(self):
        return reverse('examination_detail', args=[str(self.id)])

@receiver(post_delete, sender=Examination)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)

@receiver(post_save, sender=Examination)
def post_save_predict_image_type(sender, instance, **kwargs):
    if instance.examination_type == 'not labeled':
        img = open_image(instance.image.file)
        pred_class,pred_idx,outputs = ExaminationsConfig.learner_image_type.predict(img)
        instance.examination_type = str(pred_class)
        instance.save()
        print(pred_class)