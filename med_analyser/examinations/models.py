from django.db import models
from common.models import Doctor
from django.urls import reverse
import uuid

class Examination(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pat_name = models.CharField(verbose_name='name of patient', max_length=100)
    notes = models.TextField()
    created_by = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='examinations')
    created_on = models.DateField(verbose_name='examination creation date')

    def __str__(self):
        return 'Examination ' + self.id + ' for patient ' + self.pat_name

    def get_absolute_url(self):
        return reverse('examination_detail', args=[str(self.id)])