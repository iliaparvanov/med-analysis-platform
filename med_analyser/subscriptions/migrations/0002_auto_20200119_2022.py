# Generated by Django 2.2.9 on 2020-01-19 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='stripe_customer_id',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='stripe_subscription_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
