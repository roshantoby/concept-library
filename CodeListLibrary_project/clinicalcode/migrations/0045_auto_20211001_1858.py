# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-10-01 17:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0044_auto_20210928_1656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datasource',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='historicaldatasource',
            name='brand',
        ),
    ]
