from django.apps import apps
from django.db.models import Q, ForeignKey, Subquery, OuterRef
from django.forms.models import model_to_dict
from django.contrib.auth.models import User, Group

import re
import json
import simple_history

from . import gen_utils
from ..models.GenericEntity import GenericEntity
from ..models.PublishedGenericEntity import PublishedGenericEntity
from ..models.Tag import Tag
from ..models.CodingSystem import CodingSystem
from ..models.Concept import Concept
from ..models.ConceptReviewStatus import ConceptReviewStatus
from ..models.Component import Component
from ..models.CodeList import CodeList
from ..models.ConceptCodeAttribute import ConceptCodeAttribute
from ..models.Code import Code
from .constants import (USERDATA_MODELS, STRIPPED_FIELDS, APPROVAL_STATUS,
                        GROUP_PERMISSIONS, TAG_TYPE, HISTORICAL_HIDDEN_FIELDS,
                        CLINICAL_RULE_TYPE, CLINICAL_CODE_SOURCE)

def try_get_instance(model, **kwargs):
  '''
    Safely attempts to get an instance
  '''
  try:
    instance = model.objects.get(**kwargs)
  except:
    return None
  else:
    return instance
  
def try_get_entity_history(entity, history_id):
  '''
    Safely attempts to get an entity's historical record given an entity
    and a history id
  '''
  if not entity:
    return None
  
  try:
    instance = entity.history.get(history_id=history_id)
  except:
    return None
  else:
    return instance

def get_entity_id(primary_key):
  '''
    Splits an entity's varchar primary key into its numerical component
  '''
  entity_id = re.split('(\d.*)', primary_key)
  if len(entity_id) >= 2 and entity_id[0].isalpha() and entity_id[1].isdigit():
    return entity_id[:2]
  else:
    return False

def get_latest_entity_published(entity_id):
  '''
    Gets latest published entity given an entity id
  '''
  latest_published_entity = PublishedGenericEntity.objects.filter(
    entity_id=entity_id, approval_status=2
  ) \
  .order_by('-entity_history_id')
  
  if latest_published_entity.exists():
    return latest_published_entity.first()

  return None

def get_entity_approval_status(entity_id, historical_id):
  '''
    Gets the entity's approval status, given an entity id and historical id
  '''
  entity = try_get_instance(
    PublishedGenericEntity,
    entity_id=entity_id, 
    entity_history_id=historical_id
  )

  if entity:
    return entity.approval_status
  
  return None

def get_latest_entity_historical_id(entity_id, user):
  '''
    Gets the latest entity history id for a given entity
    and user, given the user has the permissions to access that
    particular entity
  '''
  entity = try_get_instance(GenericEntity, id=entity_id)
      
  if entity:
    if user.is_superuser:
      return int(entity.history.latest().history_id)
    
    if user:
      history = entity.history.filter(
        Q(owner=user.id) | 
        Q(
          group_id__in=user.groups.all(),
          group_access__in=[GROUP_PERMISSIONS.VIEW, GROUP_PERMISSIONS.EDIT]
        )
      ) \
      .order_by('-history_id')
      
      if history.exists():
        return history.first().history_id
  
    published = get_latest_entity_published(entity)
    if published:
      return published.history.latest().history_id

  return None

def jsonify_object(obj, remove_userdata=True, strip_fields=True, strippable_fields=None, dump=True):
  '''
    JSONifies/Dictifies instance of a model
      - removes userdata related data for safe usage within template
      - removes specific fields that are unrelated to templates e.g. SearchVectorField
      - able to strip fields from a model, given a list of field names to strip
      - able to dump to json if requested
  '''
  instance = model_to_dict(obj)
  
  if remove_userdata or strip_fields:
    for field in obj._meta.fields:
      field_type = field.get_internal_type()
      if strip_fields and field_type and field.get_internal_type() in STRIPPED_FIELDS:
        instance.pop(field.name, None)
        continue

      if strip_fields and strippable_fields is not None:
        if field.name in strippable_fields:
          instance.pop(field.name, None)
          continue

      if not remove_userdata:
        continue
      
      if not isinstance(field, ForeignKey):
        continue
      
      model = str(field.target_field.model)
      if model not in USERDATA_MODELS:
        continue
      instance.pop(field.name, None)
  
  if dump:
    return json.dumps(instance, cls=gen_utils.ModelEncoder)
  return instance

def get_tag_attribute(tag_id, tag_type):
  '''
    Returns a dict that describes a tag given its id and type
  '''
  tag = Tag.objects.filter(id=tag_id, tag_type=tag_type)
  if tag.exists():
    tag = tag.first()
    return {
      'name': tag.description,
      'value': tag.id,
      'type': tag.tag_type
    }
  
  return None

def get_coding_system_details(coding_system):
  '''
    Returns a dict that describes a coding system given that
    the coding_system parameter passed is either an obj or an int
    that references a coding_system by its codingsystem_id
  '''
  if isinstance(coding_system, int):
    coding_system = CodingSystem.objects.filter(codingsystem_id=coding_system)
    if not coding_system.exists():
      return None
    coding_system = coding_system.first()
  
  if not isinstance(coding_system, CodingSystem):
    return None
  
  return {
    'id': coding_system.codingsystem_id,
    'name': coding_system.name,
    'description': coding_system.description,
  }

def get_userdata_details(model, **kwargs):
  '''
    Attempts to return a dict that describes a userdata field e.g. a user, or a group
    in a human readable format
  '''
  hide_user_id = False
  if kwargs.get('hide_user_details'):
    hide_user_id = kwargs.pop('hide_user_details')
    
  instance = try_get_instance(model, **kwargs)
  if not instance:
    return None
  
  if isinstance(instance, Group):
    return {'id': instance.pk, 'name': instance.name}
  elif isinstance(instance, User):
    if hide_user_id:
      details = { }
    else:
      details = {'id': instance.pk}

    return details | {'username': instance.username}
  
  return details

def get_concept_component_details(concept_id, concept_history_id, aggregate_codes=False, include_codes=True, attribute_headers=None):
  '''
    [!] Note: This method ignores permissions - it should only be called from a
              a method that has previously considered accessibility

    Attempts to get all component, codelist and code data assoc.
    with a historical concept

    Args:
      concept_id {number}: The concept ID of interest
      concept_history_id {number}: The concept's historical id of interest

      aggregate_codes {boolean}: If true, will return a 'codelist' key-value pair in the result dict that
                                  describes the distinct, aggregated codes across all components

      include_codes {boolean}: If true, will return a 'codes' key-value pair within each component
                                that describes each code included in a component

      attribute_headers {list}: If a non-null list is passed, the method will attempt to find the attributes
                                associated with each code within every component (and codelist)

    Returns:
      A dict that describes the components and their details associated with this historical concept,
      and if aggregate_codes was passed, will return the distinct codelist across components
  '''

  # Try to get the Concept and its historical counterpart
  concept = try_get_instance(
    Concept, pk=concept_id
  )
  if not concept:
    return None
  
  historical_concept = try_get_entity_history(concept, concept_history_id)
  if not historical_concept:
    return None
  
  # Find the associated components (or now, rulesets) given the concept and its historical date
  components = Component.history.filter(
                                  concept__id=historical_concept.id,
                                  history_date__lte=historical_concept.history_date
                                ) \
                                .annotate(
                                  was_deleted=Subquery(
                                    Component.history.filter(
                                      id=OuterRef('id'),
                                      concept__id=historical_concept.id,
                                      history_date__lte=historical_concept.history_date,
                                      history_type='-'
                                    ) \
                                    .order_by('id', '-history_id') \
                                    .distinct('id') \
                                    .values('id')
                                  )
                                ) \
                                .exclude(was_deleted__isnull=False) \
                                .order_by('id', '-history_id') \
                                .distinct('id')
  
  if not components.exists():
    return None
  
  components_data = [ ]
  codelist_data = [ ]
  seen_codes = set()
  for component in components:
    component_data = {
      'id': component.id,
      'name': component.name,
      'logical_type': CLINICAL_RULE_TYPE(component.logical_type).name,
      'source_type': CLINICAL_CODE_SOURCE(component.component_type).name,
      'source': component.source,
    }

    # Find the codelist associated with this component
    codelist = CodeList.history.exclude(history_type='-') \
                                .filter(
                                  component__id=component.id,
                                  history_date__lte=historical_concept.history_date
                                ) \
                                .order_by('-history_date', '-history_id')

    if not codelist.exists():
      continue
    codelist = codelist.first()

    # Find the codes associated with this codelist
    codes = Code.history.filter(
                          code_list__id=codelist.id,
                          history_date__lte=historical_concept.history_date
                        ) \
                        .annotate(
                          was_deleted=Subquery(
                            Code.history.filter(
                              id=OuterRef('id'),
                              code_list__id=codelist.id,
                              history_date__lte=historical_concept.history_date,
                              history_type='-'
                            ) \
                            .order_by('code', '-history_id') \
                            .distinct('code') \
                            .values('id')
                          )
                        ) \
                        .exclude(was_deleted__isnull=False) \
                        .order_by('id', '-history_id') \
                        .distinct('id')

    component_data['code_count'] = codes.count()

    if attribute_headers is None:
      # Add each code
      codes = codes.values('id', 'code', 'description')
    else:
      # Annotate each code with its list of attribute values based on the code_attribute_headers
      codes = codes.annotate(
        attributes=Subquery(
          ConceptCodeAttribute.history.filter(
                                        concept__id=historical_concept.id,
                                        history_date__lte=historical_concept.history_date,
                                        code=OuterRef('code')
                                      )
                                      .annotate(
                                        was_deleted=Subquery(
                                          ConceptCodeAttribute.history.filter(
                                            concept__id=historical_concept.id,
                                            history_date__lte=historical_concept.history_date,
                                            code=OuterRef('code'),
                                            history_type='-'
                                          ) \
                                          .order_by('code', '-history_id') \
                                          .distinct('code') \
                                          .values('id')
                                        )
                                      )
                                      .exclude(was_deleted__isnull=False) \
                                      .order_by('id', '-history_id') \
                                      .distinct('id') \
                                      .values('attributes')
        )
      ) \
      .values('id', 'code', 'description', 'attributes')
    
    codes = list(codes)
    
    # Append codes to component if required
    if include_codes:
      component_data['codes'] = codes
    
    # Append aggregated codes if required
    if aggregate_codes:
      codes = [
        seen_codes.add(obj.get('code')) or obj
        for obj in codes
        if obj.get('code') not in seen_codes
      ]
      codelist_data += codes

    components_data.append(component_data)
  
  if aggregate_codes:
    return {
      'codelist': codelist_data,
      'components': components_data,
    }
  
  return {
    'components': components_data
  }

def get_concept_codelist(concept_id, concept_history_id, incl_logical_types=None, incl_attributes=False):
  '''
    [!] Note: This method ignores permissions - it should only be called from a
              a method that has previously considered accessibility
    
    Builds the distinct, aggregated codelist from every component associated
    with a concept, given its ID and historical id

    Args:
      concept_id {number}: The concept ID of interest
      concept_history_id {number}: The concept's historical id of interest

      incl_logical_types {int[]}: Whether to include only codes that stem from Components
                                  with that logical type

      incl_attributes {bool}: Whether to include code attributes
    
    Returns:
      A list of distinct codes associated with a concept across each of its components

  '''
  
  # Try to find the associated concept and its historical counterpart
  concept = try_get_instance(
    Concept, pk=concept_id
  )
  if not concept:
    return None
  
  historical_concept = try_get_entity_history(concept, concept_history_id)
  if not historical_concept:
    return None

  attribute_header = historical_concept.code_attribute_header
  if not incl_attributes or not isinstance(attribute_header, list) or len(attribute_header) < 1:
    attribute_header = None
  
  # Find the components associated with this concept
  components = Component.history.exclude(history_type='-') \
                                .filter(
                                  concept__id=historical_concept.id,
                                  history_date__lte=historical_concept.history_date
                                ) \
                                .annotate(
                                  was_deleted=Subquery(
                                    Component.history.filter(
                                      id=OuterRef('id'),
                                      concept__id=historical_concept.id,
                                      history_date__lte=historical_concept.history_date,
                                      history_type='-'
                                    ) \
                                    .order_by('id', '-history_id') \
                                    .distinct('id') \
                                    .values('id')
                                  )
                                ) \
                                .exclude(was_deleted__isnull=False) \
                                .order_by('id', '-history_id') \
                                .distinct('id')
  
  if not components.exists():
    return [ ]
  
  final_codelist = []
  for component in components:
    # Ignore logical types if not matched within the logical type lookup parameter
    if isinstance(incl_logical_types, list) and component.logical_type not in incl_logical_types:
      continue

    # Find the codelist associated with this component
    codelist = CodeList.history.exclude(history_type='-') \
                                .filter(
                                  component__id=component.id,
                                  history_date__lte=historical_concept.history_date
                                ) \
                                .order_by('-history_date', '-history_id')

    if not codelist.exists():
      continue
    codelist = codelist.first()

    # Find the codes associated with this codelist
    codes = Code.history.filter(
                          code_list__id=codelist.id,
                          history_date__lte=historical_concept.history_date
                        ) \
                        .annotate(
                          was_deleted=Subquery(
                            Code.history.filter(
                              id=OuterRef('id'),
                              code_list__id=codelist.id,
                              history_date__lte=historical_concept.history_date,
                              history_type='-'
                            ) \
                            .order_by('code', '-history_id') \
                            .distinct('code') \
                            .values('id')
                          )
                        ) \
                        .exclude(was_deleted__isnull=False) \
                        .order_by('id', '-history_id') \
                        .distinct('id')

    if attribute_header:
      codes = codes.annotate(
        attributes=Subquery(
          ConceptCodeAttribute.history.filter(
                                        concept__id=historical_concept.id,
                                        history_date__lte=historical_concept.history_date,
                                        code=OuterRef('code')
                                      )
                                      .annotate(
                                        was_deleted=Subquery(
                                          ConceptCodeAttribute.history.filter(
                                            concept__id=historical_concept.id,
                                            history_date__lte=historical_concept.history_date,
                                            code=OuterRef('code'),
                                            history_type='-'
                                          ) \
                                          .order_by('code', '-history_id') \
                                          .distinct('code') \
                                          .values('id')
                                        )
                                      )
                                      .exclude(was_deleted__isnull=False) \
                                      .order_by('code', '-history_id') \
                                      .distinct('code') \
                                      .values('attributes')
        )
      )
    
      final_codelist += list(codes.values('id', 'code', 'description', 'attributes'))
    else:
      final_codelist += list(codes.values('id', 'code', 'description'))
  
  seen_codes = set()
  final_codelist = [
    seen_codes.add(obj.get('code')) or obj
    for obj in final_codelist
    if obj.get('code') not in seen_codes
  ]

  return final_codelist

def get_associated_concept_codes(concept_id, concept_history_id, code_ids, incl_attributes=False):
  '''
    [!] Note: This method ignores permissions - it should only be called from a
              a method that has previously considered accessibility
    
    Retrieves the concept codes associated with the code_ids list

    Args:
      concept_id {number}: The concept ID of interest
      concept_history_id {number}: The concept's historical id of interest
      code_ids {list}: The code ids filter
      incl_attributes {bool}: Whether to include code attributes
    
    Returns:
      The codes that are present in the code ids list
    
  '''
  codelist = get_concept_codelist(concept_id, concept_history_id, incl_attributes=incl_attributes)
  codelist = [code for code in codelist if code.get('id', -1) in code_ids]
  return codelist

def get_reviewable_concept(concept_id, concept_history_id, hide_user_details=False, incl_attributes=False):
  '''
    Intended to get the reviewed / reviewable codes for a Concept
  '''
  return

def get_review_concept(concept_id, concept_history_id):
  '''
    [!] Note: This method ignores permissions - it should only be called from a
              a method that has previously considered accessibility

    Retrieves the ConceptReviewStatus instance assoc. with a Concept
    given its id and historical id

    Args:
      concept_id {number}: The concept ID of interest
      concept_history_id {number}: The concept's historical id of interest
    
    Returns:
      The associated ConceptReviewStatus instance
        
  '''
  concept = try_get_instance(
    Concept, pk=concept_id
  )
  if not concept:
    return None
  
  historical_concept = try_get_entity_history(concept, concept_history_id)
  if not historical_concept:
    return None

  return try_get_instance(
    ConceptReviewStatus,
    concept_id=historical_concept.id,
    history_id=historical_concept.history_id
  )

def get_clinical_concept_data(concept_id, concept_history_id, include_reviewed_codes=False,
                              aggregate_component_codes=False, include_component_codes=True,
                              include_attributes=False, strippable_fields=None,
                              remove_userdata=False, hide_user_details=False):
  '''
    [!] Note: This method ignores permissions - it should only be called from a
              a method that has previously considered accessibility

    Retrieves all data associated with a HistoricConcept,
    incl. a list of codes assoc. with each component, or the
    final codelist, if requested

    Args:
      concept_id {number}: The concept ID of interest
      
      concept_history_id {number}: The concept's historical id of interest

      include_reviewed_codes {boolean}: When building the data, should we pull the finalised reviewed codes?

      aggregate_component_codes {boolean}: When building the codelist, should we aggregate across components?

      include_component_codes {boolean}: When building the components, should we incl. a codelist for each component?

      include_attributes {boolean}: Should we include attributes?

      strippable_fields {list}: Whether to strip any fields from the Concept model when
                                building the concept's data result

      remove_userdata {boolean}: Whether to remove userdata related fields from the result (assoc. with each Concept)
    
    Returns:
      A dictionary that describes the concept, its components, and associated codes; constrained
      by the method parameters

  '''

  # Try to find the associated concept and its historical counterpart
  concept = try_get_instance(
    Concept, pk=concept_id
  )
  if not concept:
    return None
  
  historical_concept = try_get_entity_history(concept, concept_history_id)
  if not historical_concept:
    return None
  
  # Dictify our concept
  if not strippable_fields:
    strippable_fields = [ ]
  strippable_fields += HISTORICAL_HIDDEN_FIELDS

  concept_data = jsonify_object(
    historical_concept,
    remove_userdata=remove_userdata,
    strippable_fields=strippable_fields,
    dump=False
  )
  
  # Retrieve human readable data for our tags, collections & coding systems
  if concept_data.get('tags'):
    concept_data['tags'] = [
      get_tag_attribute(tag, tag_type=TAG_TYPE.TAG)
      for tag in concept_data['tags']
    ]

  if concept_data.get('collections'):
    concept_data['collections'] = [
      get_tag_attribute(collection, tag_type=TAG_TYPE.COLLECTION)
      for collection in concept_data['collections']
    ]

  # Clean coding system for top level field use
  concept_data.pop('coding_system')
  
  # If userdata is requested, try to grab all related 
  if not remove_userdata:
    for field in historical_concept._meta.fields:
      if field.name not in concept_data:
        continue

      if not isinstance(field, ForeignKey):
        continue
      
      model = field.target_field.model
      if str(model) not in USERDATA_MODELS:
        continue

      concept_data[field.name] = get_userdata_details(
        model, pk=concept_data[field.name], hide_user_details=hide_user_details
      )
  
  # Clean data if required
  if not concept_data.get('is_deleted'):
    concept_data.pop('is_deleted')
    concept_data.pop('deleted_by')
    concept_data.pop('deleted')

  # Build codelist and components from concept (modified by params)
  attribute_headers = concept_data.pop('code_attribute_header', None) if include_attributes else None
  attribute_headers = attribute_headers if isinstance(attribute_headers, list) and len(attribute_headers) > 0 else None
  components_data = get_concept_component_details(
    concept_id,
    concept_history_id,
    aggregate_codes=aggregate_component_codes,
    include_codes=include_component_codes,
    attribute_headers=attribute_headers
  )

  # Only append header attribute if not null
  if attribute_headers is not None:
    concept_data['code_attribute_headers'] = attribute_headers
  
  result = {
    'concept_id': concept_id,
    'concept_version_id': concept_history_id,
    'coding_system': get_coding_system_details(historical_concept.coding_system),
    'details': concept_data,
    'components': components_data.get('components'),
  }

  # Apply aggregated codes if required
  if aggregate_component_codes:
    result['aggregated_component_codes'] = components_data.get('codelist')

  # Build the final, reviewed codelist if required
  if include_reviewed_codes:
    result['codelist'] = get_concept_codelist(concept_id, concept_history_id, incl_logical_types=[CLINICAL_RULE_TYPE.INCLUDE.value], incl_attributes=include_attributes)
  
  return result

def append_coding_system_data(systems):
  '''
    Appends the number of available codes within a Coding System's
    codelist as well as whether it is searchable
      - This is used primarily for the create/update page to determine
        whether a search rule is applicable
    
    Args:
      systems {list[dict]} A list of dicts that contains the coding systems of interest
                            e.g. {name: (str), value: (int)} where value is the pk
      
    Returns:
      A list of dicts that has the number of codes/searchable status appended,
      as defined by their code reference tables
  '''
  for i, system in enumerate(systems):
    try:
      coding_system = CodingSystem.objects.get(codingsystem_id=system.get('value'))
      table = coding_system.table_name.replace('clinicalcode_', '')
      codes = apps.get_model(app_label='clinicalcode', model_name=table)
      count = codes.objects.count() > 0
      systems[i]['code_count'] = count
      systems[i]['can_search'] = count
    except:
      continue
  
  return systems

def modify_entity_change_reason(entity, reason):
  '''
    Modify an entity's HistoricalRecord to reflect the change reason on update
  '''
  if entity is None:
    return
  
  reason = (reason[:98] + '..') if len(reason) > 98 else reason
  simple_history.utils.update_change_reason(entity, reason)