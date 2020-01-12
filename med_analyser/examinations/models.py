from django.db import models
from common.models import Doctor

class Examination(models.Model):
    pat_name = models.CharField(verbose_name='name of patient', max_length=100)
    notes = models.TextField()
    created_by = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='examinations')
    created_on = models.DateField(verbose_name='examination creation date')

    def __str__(self):
        return 'Examination ' + self.pk + ' for patient ' + self.pat_name