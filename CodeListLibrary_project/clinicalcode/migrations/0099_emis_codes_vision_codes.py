# Generated by Django 4.0.10 on 2023-05-05 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0098_brand_footer_images_historicalbrand_footer_images'),
    ]

    # EMIS & Vision codes are already on prod
    operations = []
    
    # operations = [
    #     migrations.CreateModel(
    #         name='EMIS_CODES',
    #         fields=[
    #             ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
    #             ('code', models.CharField(blank=True, max_length=50, null=True)),
    #             ('description', models.CharField(blank=True, max_length=255, null=True)),
    #             ('field', models.CharField(blank=True, max_length=255, null=True)),
    #             ('version', models.CharField(blank=True, max_length=50, null=True)),
    #             ('import_date', models.DateTimeField(blank=True, null=True)),
    #             ('created_date', models.DateTimeField(blank=True, null=True)),
    #             ('effective_from', models.DateTimeField(blank=True, null=True)),
    #             ('effective_to', models.DateField(blank=True, null=True)),
    #             ('avail_from_dt', models.DateField(blank=True, null=True)),
    #         ],
    #     ),
    #     migrations.CreateModel(
    #         name='VISION_CODES',
    #         fields=[
    #             ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
    #             ('code', models.CharField(blank=True, max_length=50, null=True)),
    #             ('description', models.CharField(blank=True, max_length=255, null=True)),
    #             ('field', models.CharField(blank=True, max_length=255, null=True)),
    #             ('version', models.CharField(blank=True, max_length=50, null=True)),
    #             ('import_date', models.DateTimeField(blank=True, null=True)),
    #             ('created_date', models.DateTimeField(blank=True, null=True)),
    #             ('effective_from', models.DateTimeField(blank=True, null=True)),
    #             ('effective_to', models.DateField(blank=True, null=True)),
    #             ('avail_from_dt', models.DateField(blank=True, null=True)),
    #         ],
    #     ),
    # ]