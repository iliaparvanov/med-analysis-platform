# Generated by Django 2.2.10 on 2020-02-10 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_doctor_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='subscription',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscriptions.Subscription'),
        ),
    ]
