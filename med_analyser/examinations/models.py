from django.db import models
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from common.models import Doctor
from .apps import ExaminationsConfig
import uuid, io
from datetime import date
from fastai.vision import open_image
from fastai.vision.image import Image as FAIImage
from fastai.callbacks.hooks import *
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from apscheduler.schedulers.background import BackgroundScheduler


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
    heatmap = models.ImageField(upload_to='examination_heatmaps/', blank=True, null=True)
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

def generate_heatmap(examination_instance, img, learner, pred_idx):
    m = learner.model.eval()
    xb,_ = learner.data.one_item(img)
    xb_denormed = FAIImage(learner.data.denorm(xb)[0])

    def hooked_backward(pred_idx, x_batch):
        with hook_output(m[0]) as hook_a: 
            with hook_output(m[0], grad=True) as hook_g:
                preds = m(x_batch)
                preds[0,int(pred_idx)].backward()
        return hook_a,hook_g
    
    hook_a,hook_g = hooked_backward(pred_idx, xb)
    heatmap = hook_a.stored[0].mean(0)

    # plot the heatmap on top of image
    _,ax = plt.subplots()
    xb_denormed.show(ax)
    ax.imshow(heatmap, alpha=0.6, extent=(0,xb.shape[2],xb.shape[3],0), interpolation='bilinear', cmap='magma')

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg')
    examination_instance.heatmap.save(str(examination_instance.id) + "_heatmap.jpg", File(buf), save=True)


@receiver(post_save, sender=Examination)
def infer_findings(sender, instance, created,**kwargs):
    if created: 
        # delete all existing inferred findings
        inferred_findings = InferredFinding.objects.filter(examination=instance)
        inferred_findings.delete()

        # infer new findings
        img = open_image(instance.image.file)
        try:
            any_findings_learner = ExaminationsConfig.learners_findings[instance.image_type.label]['any_findings']
            pred_class,pred_idx,outputs = any_findings_learner.predict(img)
            inferred_finding = InferredFinding(examination=instance, finding=Finding.objects.get(is_no_finding=True), certainty=outputs[1])
            inferred_finding.save()

            if inferred_finding.certainty < 0.5:
                generate_heatmap(instance, img, any_findings_learner, pred_idx)
            
            findings_learner = ExaminationsConfig.learners_findings[instance.image_type.label]['findings']
            pred_class,pred_idx,outputs = findings_learner.predict(img)
            for c, output in zip(findings_learner.data.classes, outputs):
                inferred_finding = InferredFinding(examination=instance, finding=Finding.objects.get(label=c), certainty=output)
                inferred_finding.save()
            
        except KeyError:
            print('No model for this image type')

@receiver(post_delete, sender=Examination)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
