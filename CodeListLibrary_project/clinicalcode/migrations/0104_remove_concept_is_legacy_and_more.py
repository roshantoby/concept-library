# Generated by Django 4.0.10 on 2023-05-11 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinicalcode', '0103_alter_genericentity_publish_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concept',
            name='is_legacy',
        ),
        migrations.RemoveField(
            model_name='historicalconcept',
            name='is_legacy',
        ),
        migrations.AddField(
            model_name='concept',
            name='phenotype_owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_concepts', to='clinicalcode.genericentity'),
        ),
        migrations.AddField(
            model_name='historicalconcept',
            name='phenotype_owner',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='clinicalcode.genericentity'),
        ),
    ]