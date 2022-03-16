# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2020-12-03 13:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clinicalcode', '0009_auto_20201109_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublishedPhenotype',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('phenotype_history_id', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by',
                 models.ForeignKey(
                     null=True,
                     on_delete=django.db.models.deletion.SET_NULL,
                     related_name='ph_publication_owner',
                     to=settings.AUTH_USER_MODEL)),
                ('phenotype',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='clinicalcode.Phenotype')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='publishedphenotype',
            unique_together=set([('phenotype', 'phenotype_history_id')]),
        ),
    ]
