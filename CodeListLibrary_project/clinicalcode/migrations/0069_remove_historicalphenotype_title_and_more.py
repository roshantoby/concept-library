# Generated by Django 4.0.7 on 2022-10-07 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0068_phenotypeworkingset_historicalpublishedworkingset_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalphenotype',
            name='title',
        ),
        migrations.RemoveField(
            model_name='phenotype',
            name='title',
        ),
    ]
