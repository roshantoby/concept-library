from django.db import models
from django.contrib.auth.models import User, Group
from simple_history.models import HistoricalRecords
from TimeStampedModel import TimeStampedModel


class Brand(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    logo_path = models.CharField(max_length=250)
    css_path = models.CharField(max_length=250, blank=True, null=True)
    website = models.URLField(max_length=1000, blank=True, null=True)  # http website url
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="brand_owner")
    groups = models.ManyToManyField(Group, related_name="brand_groups")

    history = HistoricalRecords()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
    
   












