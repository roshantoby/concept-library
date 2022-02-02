# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2020-04-08 11:50


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0007_auto_20200403_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='description',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='concept',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='concept',
            name='secondary_publication_links',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='concept',
            name='validation_description',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='historicalconcept',
            name='description',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='historicalconcept',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='historicalconcept',
            name='secondary_publication_links',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='historicalconcept',
            name='validation_description',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='historicalworkingset',
            name='author',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='historicalworkingset',
            name='description',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='historicalworkingset',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='historicalworkingset',
            name='publication',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='historicalworkingset',
            name='secondary_publication_links',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='workingset',
            name='author',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='workingset',
            name='description',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='workingset',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='workingset',
            name='publication',
            field=models.CharField(max_length=3000),
        ),
        migrations.AlterField(
            model_name='workingset',
            name='secondary_publication_links',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
    ]
