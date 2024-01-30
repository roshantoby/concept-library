# Generated by Django 4.1.10 on 2024-01-30 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0110_read_cd_cv2_scd_readv2_defn_ln_gin_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClinicalAnatomicalCategoryEdge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClinicalDiseaseCategoryEdge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClinicalSpecialityCategoryEdge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClinicalSpecialityCategoryNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=510, unique=True)),
                ('children', models.ManyToManyField(blank=True, related_name='parents', through='clinicalcode.ClinicalSpecialityCategoryEdge', to='clinicalcode.clinicalspecialitycategorynode')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='clinicalspecialitycategoryedge',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_edges', to='clinicalcode.clinicalspecialitycategorynode'),
        ),
        migrations.AddField(
            model_name='clinicalspecialitycategoryedge',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children_edges', to='clinicalcode.clinicalspecialitycategorynode'),
        ),
        migrations.CreateModel(
            name='ClinicalDiseaseCategoryNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=510)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('code_id', models.IntegerField(blank=True, null=True)),
                ('children', models.ManyToManyField(blank=True, related_name='parents', through='clinicalcode.ClinicalDiseaseCategoryEdge', to='clinicalcode.clinicaldiseasecategorynode')),
                ('coding_system', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='disease_categories', to='clinicalcode.codingsystem')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='clinicaldiseasecategoryedge',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_edges', to='clinicalcode.clinicaldiseasecategorynode'),
        ),
        migrations.AddField(
            model_name='clinicaldiseasecategoryedge',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children_edges', to='clinicalcode.clinicaldiseasecategorynode'),
        ),
        migrations.CreateModel(
            name='ClinicalAnatomicalCategoryNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=510, unique=True)),
                ('atlas_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('children', models.ManyToManyField(blank=True, related_name='parents', through='clinicalcode.ClinicalAnatomicalCategoryEdge', to='clinicalcode.clinicalanatomicalcategorynode')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='clinicalanatomicalcategoryedge',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_edges', to='clinicalcode.clinicalanatomicalcategorynode'),
        ),
        migrations.AddField(
            model_name='clinicalanatomicalcategoryedge',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children_edges', to='clinicalcode.clinicalanatomicalcategorynode'),
        ),
    ]
