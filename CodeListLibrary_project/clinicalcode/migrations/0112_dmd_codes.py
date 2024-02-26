# Generated by Django 4.1.10 on 2024-02-13 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0111_historicaltemplate_hide_on_create_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DMD_CODES',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
