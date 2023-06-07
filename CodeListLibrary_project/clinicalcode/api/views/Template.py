from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from ...models import *
from ...entity_utils import permission_utils
from ...entity_utils import api_utils
from ...entity_utils import template_utils
from ...entity_utils import constants

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_templates(request):
  '''
  
  '''
  if permission_utils.is_member(request.user, 'ReadOnlyUsers') or settings.CLL_READ_ONLY:
    return Response(
      data={
        'message': 'Permission denied'
      },
      content_type='json',
      status=status.HTTP_403_FORBIDDEN
    )
    
  templates = Template.objects.all()
  
  result = []
  for template in templates:
    result.append({
      'id': template.id,
      'version_id': template.template_version,
      'name': template.name,
      'description': template.description,
      'versions': api_utils.get_template_versions(template.id)
    })

  return Response(
    data=result,
    status=status.HTTP_200_OK
  )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_template_version_history(request, template_id):
  '''
  
  '''
  if permission_utils.is_member(request.user, 'ReadOnlyUsers') or settings.CLL_READ_ONLY:
    return Response(
      data={
        'message': 'Permission denied'
      },
      content_type='json',
      status=status.HTTP_403_FORBIDDEN
    )
  
  template = Template.objects.filter(id=template_id)
  if not template.exists():
    return Response(
      data={
        'message': 'Template with specified id does not exist'
      },
      content_type='json',
      status=status.HTTP_404_NOT_FOUND
    )
  template = template.first()

  return Response(
    data={
      'id': template.id,
      'versions': api_utils.get_template_versions(template.id)
    },
    status=status.HTTP_200_OK
  )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_template(request, template_id, version_id=None):
  '''
  
  '''
  if permission_utils.is_member(request.user, 'ReadOnlyUsers') or settings.CLL_READ_ONLY:
    return Response(
      data={
        'message': 'Permission denied'
      },
      content_type='json',
      status=status.HTTP_403_FORBIDDEN
    )
  
  template = Template.objects.filter(id=template_id)
  if not template.exists():
    return Response(
      data={
        'message': 'Template with specified id does not exist'
      },
      content_type='json',
      status=status.HTTP_404_NOT_FOUND
    )
  template = template.first()
  
  if version_id:
    template = template.history.filter(template_version=version_id)
    if not template.exists():
        return Response(
            data={
                'message': 'Template with specified version id does not exist'
            },
            content_type='json',
            status=status.HTTP_404_NOT_FOUND
        )
    template = template.latest()
    
  merged_definition = template_utils.get_merged_definition(template)
  template_fields = template_utils.try_get_content(merged_definition, 'fields')
  
  formatted_fields = []
  for field, definition in template_fields.items():
    is_active = template_utils.try_get_content(definition, 'active')
    if not is_active:
      continue

    validation = template_utils.try_get_content(definition, 'validation')
    if validation is None:
      continue

    field_type = template_utils.try_get_content(validation, 'type')
    if field_type is None:
      continue

    field_data = {
      'field_name': field,
      'field_type': field_type,
      'field_description': template_utils.try_get_content(definition, 'description'),
      'field_mandatory': template_utils.try_get_content(validation, 'mandatory', default=False)
    }

    if field_type == 'enum':
      options = template_utils.try_get_content(validation, 'options')
      if options:
        field_data['field_inputs'] = [
          { 'id': key, 'value': value } for key, value in options.items()
        ]

    formatted_fields.append(field_data)
  
  return Response(
    data={
      'id': template.id,
      'version_id': template.template_version,
      'template': formatted_fields
    },
    status=status.HTTP_200_OK
  )
