# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2021-08-06 13:31


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0032_auto_20210719_2015'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='brand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_source_brand', to='clinicalcode.Brand'),
        ),
        migrations.AddField(
            model_name='historicaldatasource',
            name='brand',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='clinicalcode.Brand'),
        ),
    ]
