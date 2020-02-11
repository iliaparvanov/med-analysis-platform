from django.db import models
from common.models import Doctor
from django.urls import reverse
from django.conf import settings
import uuid
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver

class ImageType(models.Model):
    label = models.CharField(max_length=15)
    human_readable = models.CharField(max_length=25)

    def __str__(self):
        return self.human_readable

class Finding(models.Model):
    label = models.CharField(max_length=25)
    is_no_finding = models.BooleanField(verbose_name='does this finding represent that there were no findings in image', default=False)

    def __str__(self):
        return self.label

class Examination(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pat_name = models.CharField(verbose_name='name of patient', max_length=100)
    image = models.ImageField(upload_to='examination_images/', blank=True)
    notes = models.TextField()
    image_type = models.ForeignKey(ImageType, on_delete=models.SET_NULL, null=True)
    findings = models.ManyToManyField(Finding, through='InferredFinding')
    created_by = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='examinations')
    created_on = models.DateField(verbose_name='examination creation date')

    def __str__(self):
        return 'Examination ' + str(self.id) + ' for patient ' + self.pat_name

    def get_absolute_url(self):
        return reverse('examination_detail', args=[str(self.id)])

class InferredFinding(models.Model):
    finding = models.ForeignKey(Finding, on_delete=models.CASCADE)
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)
    certainty = models.FloatField()

@receiver(post_delete, sender=Examination)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
