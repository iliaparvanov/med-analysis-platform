from django.db import models
from common.models import Doctor
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
import uuid
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from datetime import date
from .apps import ExaminationsConfig
from fastai.vision.image import open_image 

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
    conducted_on = models.DateField(default=timezone.now)
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

    def __str__(self):
        return str(self.finding)

    def certainty_as_pct(self):
        return round(self.certainty*100, 2)

    def certainty_as_pct_to_100(self):
        return round(100-(self.certainty*100), 2)

class ConfirmedFinding(models.Model):
    finding = models.ForeignKey(Finding, on_delete=models.CASCADE)
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)
    training_complete = models.BooleanField(verbose_name='the model was trained on this finding', default=False)
    marked_for_training = models.BooleanField(verbose_name='the model will soon be trained on this finding', default=False)

    def __str__(self):
        return str(self.finding)

@receiver(post_save, sender=Examination)
def infer_findings(sender, instance,  **kwargs):
    # delete all existing inferred findings
    inferred_findings = InferredFinding.objects.filter(examination=instance)
    inferred_findings.delete()

    # infer new findings
    img = open_image(instance.image.file)
    try:
        any_findings_learner = ExaminationsConfig.learners_findings[instance.image_type.label]['any_findings']
        pred_class,pred_idx,outputs = any_findings_learner.predict(img)
        print(pred_class)
        inferred_finding = InferredFinding(examination=instance, finding=Finding.objects.get(is_no_finding=True), certainty=outputs[1])
        inferred_finding.save()
        
        inferred_finding = InferredFinding(examination=instance, finding=Finding.objects.get(label='No Finding'), certainty=outputs[1])
        findings_learner = ExaminationsConfig.learners_findings[instance.image_type.label]['findings']
        pred_class,pred_idx,outputs = findings_learner.predict(img)
        for c, output in zip(findings_learner.data.classes, outputs):
            inferred_finding = InferredFinding(examination=instance, finding=Finding.objects.get(label=c), certainty=output)
            inferred_finding.save()
        
    except KeyError:
        pass

@receiver(post_delete, sender=Examination)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
