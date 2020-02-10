from django.db import models
from common.models import Doctor
from django.urls import reverse
import uuid
from cloudinary.models import CloudinaryField
import cloudinary
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from urllib.request import urlopen
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

# @receiver(pre_delete, sender=Examination)
# def examination_delete(sender, instance, **kwargs):
#     if instance.image:
#         cloudinary.uploader.destroy(instance.image.public_id)

# @receiver(post_save, sender=Examination)
# def post_save_predict_image_type(sender, instance, **kwargs):
#     if instance.examination_type == 'not labeled':
#         img = open_image(urlopen(instance.image.url))
#         pred_class,pred_idx,outputs = ExaminationsConfig.learner_image_type.predict(img)
#         instance.examination.type = 'chest'
#         print(pred_class)