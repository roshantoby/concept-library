# Generated by Django 4.0.10 on 2023-05-10 15:32

import clinicalcode.entity_utils.constants
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0102_alter_genericentity_publish_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericentity',
            name='publish_status',
            field=models.IntegerField(choices=[('ANY', -1), ('REQUESTED', 0), ('PENDING', 1), ('APPROVED', 2), ('REJECTED', 3)], default=clinicalcode.entity_utils.constants.APPROVAL_STATUS['ANY'], null=True),
        ),
        migrations.AlterField(
            model_name='historicalgenericentity',
            name='publish_status',
            field=models.IntegerField(choices=[('ANY', -1), ('REQUESTED', 0), ('PENDING', 1), ('APPROVED', 2), ('REJECTED', 3)], default=clinicalcode.entity_utils.constants.APPROVAL_STATUS['ANY'], null=True),
        ),
    ]