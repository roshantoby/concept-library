# Generated by Django 4.1.10 on 2023-09-13 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0108_alter_concept_group_access_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='read_cd_cv2_scd',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='read_cd_cv3_terms_scd',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
