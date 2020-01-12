# Generated by Django 2.2.9 on 2020-01-12 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0002_auto_20200112_1636'),
    ]

    operations = [
        migrations.CreateModel(
            name='Examination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name of patient', models.CharField(max_length=100)),
                ('notes', models.TextField()),
                ('examination creation date', models.DateField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examinations', to='common.Doctor')),
            ],
        ),
    ]
