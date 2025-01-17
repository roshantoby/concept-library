# Generated by Django 2.2.24 on 2022-03-21 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0055_auto_20220222_0634'),
    ]

    operations = [
        migrations.CreateModel(
            name='CTV3_CODES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GPRD_PRODUCT_CODES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ICD_11_CODES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ICD_9_CODES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ICPC_2_CODES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MULTILEX_CODES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OXMIS_CODES',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('version', models.CharField(blank=True, max_length=50, null=True)),
                ('import_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('effective_from', models.DateTimeField(blank=True, null=True)),
                ('effective_to', models.DateField(blank=True, null=True)),
                ('avail_from_dt', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
