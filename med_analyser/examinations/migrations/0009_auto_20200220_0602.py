# Generated by Django 2.2.10 on 2020-02-20 04:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('examinations', '0008_examination_conducted_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examination',
            name='conducted_on',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]