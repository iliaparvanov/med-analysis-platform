# Generated by Django 2.2.10 on 2020-02-17 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_auto_20200210_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospital',
            name='email_domain',
            field=models.CharField(default='blank.com', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]