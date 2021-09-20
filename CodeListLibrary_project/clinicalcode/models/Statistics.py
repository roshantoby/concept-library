from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from clinicalcode.models.TimeStampedModel import TimeStampedModel
from django.contrib.postgres.fields import JSONField

class Statistics(TimeStampedModel):

    org = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    stat = JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="stat_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="stat_updated")

    history = HistoricalRecords()
    
    
    class Meta:
        ordering = ('org',)
        
        
    def __str__(self):
        return self.org