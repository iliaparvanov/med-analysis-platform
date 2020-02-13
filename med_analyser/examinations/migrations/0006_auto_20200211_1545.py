# Generated by Django 2.2.10 on 2020-02-11 13:45

from django.db import migrations
from examinations.apps import ExaminationsConfig

def from_learners_add_findings(apps, schema_editor):
    Finding = apps.get_model('examinations', 'Finding')
    for learner in ExaminationsConfig.learners_findings:
        for c in ExaminationsConfig.learners_findings[learner].data.classes:
            f = Finding(label=c)
            if c.lower() == 'no finding':
                f.is_no_finding = True
            f.save()

def from_learners_remove_findings(apps, schema_editor):
    Finding = apps.get_model('examinations', 'Finding')
    for learner in ExaminationsConfig.learners_findings:
        for c in ExaminationsConfig.learners_findings[learner].data.classes:
            f = Finding.objects.get(label=c)
            f.delete() 

class Migration(migrations.Migration):

    dependencies = [
        ('examinations', '0005_auto_20200211_1521'),
    ]

    operations = [
        migrations.RunPython(from_learners_add_findings, from_learners_remove_findings)
    ]