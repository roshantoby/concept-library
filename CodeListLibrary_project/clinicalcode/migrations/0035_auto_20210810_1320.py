# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-08-10 12:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0034_auto_20210806_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='concept',
            name='friendly_id',
            field=models.CharField(default=b'C', editable=False, max_length=50),
        ),
        migrations.AddField(
            model_name='historicalconcept',
            name='friendly_id',
            field=models.CharField(default=b'C', editable=False, max_length=50),
        ),
    ]
