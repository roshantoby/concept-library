from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords
from clinicalcode.models.TimeStampedModel import TimeStampedModel
from .Phenotype import Phenotype
from .DataSource import DataSource


class PhenotypeDataSourceMap(TimeStampedModel):
    phenotype = models.ForeignKey(Phenotype)
    datasource = models.ForeignKey(DataSource)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="phenotypedatasourcemaps_created")

    history = HistoricalRecords()