# Generated by Django 2.2.10 on 2020-02-11 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('examinations', '0003_examination_examination_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Finding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=25)),
                ('is_no_finding', models.BooleanField(default=False, verbose_name='does this finding represent that there were no findings in image')),
            ],
        ),
        migrations.CreateModel(
            name='ImageType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=15)),
                ('human_readable', models.CharField(max_length=25)),
            ],
        ),
        migrations.RemoveField(
            model_name='examination',
            name='examination_type',
        ),
        migrations.AlterField(
            model_name='examination',
            name='image',
            field=models.ImageField(blank=True, upload_to='examination_images/'),
        ),
        migrations.CreateModel(
            name='InferredFinding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certainty', models.FloatField()),
                ('examination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='examinations.Examination')),
                ('finding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='examinations.Finding')),
            ],
        ),
        migrations.AddField(
            model_name='examination',
            name='findings',
            field=models.ManyToManyField(through='examinations.InferredFinding', to='examinations.Finding'),
        ),
        migrations.AddField(
            model_name='examination',
            name='image_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='examinations.ImageType'),
        ),
    ]