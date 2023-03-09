from django.contrib.auth.models import Group, User
from django.db.models import JSONField
from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.postgres.fields import ArrayField

from .TimeStampedModel import TimeStampedModel
from .Brand import Brand
from clinicalcode.constants import *
from ..entity_utils import constants
from .EntityClass import EntityClass

class Template(TimeStampedModel):
    '''
        Template
            @desc describes the structure of the data for that type of generic entity
                and holds statistics information e.g.
                    - count of each entity within this template
                    - count of tag/collection/datasource/coding system/

                also holds information relating to represents the filterable fields as a hasmap to improve performance
                as well as ensuring order is kept through creating a 'layout_order' field and an 'order' field within
                the template definition
    '''

    ''' Metadata '''
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    definition = JSONField(blank=True, null=True, default=dict)
    entity_class = models.ForeignKey(EntityClass, on_delete=models.SET_NULL, null=True, related_name="entity_class_type")
    template_version = models.IntegerField(null=True, editable=False)

    ''' Instance data '''
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="template_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="template_updated")
    history = HistoricalRecords()

    def save(self,  *args, **kwargs):
        '''
            [!] Note: Historical records are only created if the 'version' field within the template definition is changed
                      otherwise, the same row is updated - see ./admin.py for more
        '''
                  
        super(Template, self).save(*args, **kwargs)
    
    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret
    
    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
