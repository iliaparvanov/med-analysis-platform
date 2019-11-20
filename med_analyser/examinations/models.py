from django.db import models

class Radiologist(models.Model):
    pass

class Examination(models.Model):
    pat_name = models.CharField(name='name of patient', max_length=100)
    notes = models.TextField()
    created_by = models.ForeignKey(Radiologist, on_delete=models.CASCADE)
    created_on = models.DateField(name='examination creation date')

    def __str__(self):
        return 'Examination ' + self.pk + ' for patient ' + self.pat_name