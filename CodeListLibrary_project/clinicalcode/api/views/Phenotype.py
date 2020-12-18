from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.http.response import Http404
from django.db.models import Q

from ..serializers import *

from ...models.Concept import Concept
from ...models.Tag import Tag
from ...models.Phenotype import Phenotype
from ...models.PhenotypeTagMap import PhenotypeTagMap
from ...models.DataSource import DataSource
from ...models.Brand import Brand
from ...models.PublishedPhenotype import PublishedPhenotype

from django.contrib.auth.models import User

from ...db_utils import *
from ...viewmodels.js_tree_model import TreeModelManager
from ...permissions import *

from collections import OrderedDict
from django.core.exceptions import PermissionDenied
import json
from clinicalcode.context_processors import clinicalcode
from collections import OrderedDict as ordr 
from ...utils import *
from numpy.distutils.fcompiler import none

from View import *
from django.core import serializers
from datetime import datetime
from django.core.validators import URLValidator
from View import chk_group, chk_group_access, chk_tags, chk_world_access
from django.db.models.aggregates import Max

@api_view(['POST'])
def api_phenotype_create(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if is_member(request.user, group_name='ReadOnlyUsers'):
        raise PermissionDenied

    validate_access_to_create()
    user_groups = getGroups(request.user)
    if request.method == 'POST':
        errors_dict = {}
        is_valid = True

        known_phenotypes = set(get_visible_phenotypes(request.user).exclude(is_deleted=True).values_list('phenotype_id', flat=True))
        new_phenotype_id = request.data.get('phenotype_id')
        if new_phenotype_id in known_phenotypes:
          return Response(
            data = {'phenotype_id': 'Phenotype_id must be unique: submitted id is already found'}, 
            content_type="json", 
            status=status.HTTP_406_NOT_ACCEPTABLE
          )

        new_phenotype = Phenotype()
        new_phenotype.phenotype_id = new_phenotype_id
        new_phenotype.title = request.data.get('title')
        new_phenotype.name = request.data.get('name')
        new_phenotype.author = request.data.get('author')
        new_phenotype.layout = request.data.get('layout')
        new_phenotype.type = request.data.get('type')
        new_phenotype.validation = request.data.get('validation')
        new_phenotype.valid_event_data_range_start = request.data.get('valid_event_data_range_start')
        new_phenotype.valid_event_data_range_end = request.data.get('valid_event_data_range_end')
        new_phenotype.sex = request.data.get('sex')
        new_phenotype.status = request.data.get('status')
        new_phenotype.hdr_created_date = request.data.get('hdr_created_date')
        new_phenotype.hdr_modified_date = request.data.get('hdr_modified_date')
        new_phenotype.publications = request.data.get('publications')
        new_phenotype.publication_doi = request.data.get('publication_doi')
        new_phenotype.publication_link = request.data.get('publication_link')
        new_phenotype.secondary_publication_links = request.data.get('secondary_publication_links')
        new_phenotype.source_reference = request.data.get('source_reference') 
        new_phenotype.citation_requirements = request.data.get('citation_requirements')
        new_phenotype.concept_informations = request.data.get('concept_informations')
        
        new_phenotype.created_by = request.user        
        new_phenotype.owner_access = Permissions.EDIT
        new_phenotype.owner_id = request.user.id

        concept_ids_list = request.data.get('concept_informations')
        if concept_ids_list is None or not isinstance(concept_ids_list, list):
            errors_dict['concept_informations'] = 'concept_informations must have a valid concept ids list'
        else:
            if len(concept_ids_list) == 0:
                errors_dict['concept_informations'] = 'concept_informations must have a valid non-empty concept ids list'
            else:
                if not chkListIsAllIntegers(concept_ids_list):
                    errors_dict['concept_informations'] = 'concept_informations must have a valid concept ids list'
                else: 
                    if len(set(concept_ids_list)) != len(concept_ids_list):
                        errors_dict['concept_informations'] = 'concept_informations must have a unique concept ids list'
                    else:
                        permittedConcepts = get_list_of_visible_concept_ids(get_visible_live_or_published_concept_versions(request , exclude_deleted = True)
                                                                            , return_id_or_history_id="id")
                        if not (set(concept_ids_list).issubset(set(permittedConcepts))):
                            errors_dict['concept_informations'] = 'invalid concept_informations ids list, all concept ids must be valid and accessible by user'
                        else:
                            #print('')
                            concept_informations = getPhenotypeConceptJson(concept_ids_list) #concept.history.latest.pkid
                            new_phenotype.concept_informations = concept_informations

        # group id 
        is_valid_data, err, ret_value = chk_group(request.data.get('group') , user_groups)
        if is_valid_data:
            group_id = ret_value
            if group_id is None or group_id == "0":
                new_phenotype.group_id = None
                new_phenotype.group_access = 1
            else:
                new_phenotype.group_id = group_id
                
                is_valid_data, err, ret_value = chk_group_access(request.data.get('group_access'))
                if is_valid_data:
                    new_phenotype.group_access = ret_value
                else:
                    errors_dict['group_access'] = err
        else:
            errors_dict['group'] = err
      
        # handle world-access
        is_valid_data, err, ret_value = chk_world_access(request.data.get('world_access'))
        if is_valid_data:
            new_phenotype.world_access = ret_value
        else:
            errors_dict['world_access'] = err        

        # handling tags  
        tags = request.data.get('tags')
        is_valid_data, err, ret_value = chk_tags(request.data.get('tags'))
        if is_valid_data:
            tags = ret_value
        else:
            errors_dict['tags'] = err  
           
        # Validation
        errors_pt = {}
        if bool(errors_dict):
            is_valid = False
            
        is_valid_pt = True
        is_valid_pt, errors_pt = isValidPhenotype(request, new_phenotype)
        
        if not is_valid or not is_valid_pt:          
            errors_dict.update(errors_pt)
            return Response(
              data = errors_dict, 
              content_type="json", 
              status=status.HTTP_406_NOT_ACCEPTABLE
            )
        else:
            new_phenotype.save()
            created_pt = Phenotype.objects.get(pk=new_phenotype.pk)
            created_pt.history.latest().delete() 
             
            tag_ids = tags
            if tag_ids:
                new_tag_list = [int(i) for i in tag_ids]
            if tag_ids:
                for tag_id_to_add in new_tag_list:
                    PhenotypeTagMap.objects.get_or_create(phenotype=new_phenotype, tag=Tag.objects.get(id=tag_id_to_add), created_by=request.user)
            
            datasource_ids_list = request.data.get('data_sources')
            for cur_id in datasource_ids_list:
              new_phenotype.data_sources.add(
                int(cur_id)
              )

            created_pt.changeReason = "Created from API"
            created_pt.save()   
            data = {
              'message': 'Phenotype created successfully',
              'id': created_pt.pk
            }
            return Response(
              data = data, 
              content_type="text/json-comment-filtered", 
              status=status.HTTP_201_CREATED
            )

@api_view(['PUT'])
def api_phenotype_update(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if is_member(request.user, group_name='ReadOnlyUsers'):
        raise PermissionDenied
    
    validate_access_to_create()
    user_groups = getGroups(request.user)
    if request.method == 'PUT':
        errors_dict = {}
        is_valid = True

        phenotype_id = request.data.get('id') 
        if not isInt(phenotype_id):
            errors_dict['id'] = 'phenotype_id must be a valid id.' 
            return Response(
              data = errors_dict, 
              content_type="json", 
              status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        if Phenotype.objects.filter(pk=phenotype_id).count() == 0: 
            errors_dict['id'] = 'phenotype_id not found.' 
            return Response( 
              data = errors_dict, 
              content_type="json", 
              status=status.HTTP_406_NOT_ACCEPTABLE
            )
        if not allowed_to_edit(request.user, Phenotype, phenotype_id):
            errors_dict['id'] = 'phenotype_id must be a valid accessible phenotype id.' 
            return Response( 
              data = errors_dict, 
              content_type="json", 
              status=status.HTTP_406_NOT_ACCEPTABLE
            )
        
        update_phenotype = Phenotype.objects.get(pk=phenotype_id)
        update_phenotype.phenotype_id = request.data.get('phenotype_id')
        update_phenotype.title = request.data.get('title')
        update_phenotype.name = request.data.get('name')
        update_phenotype.author = request.data.get('author')
        update_phenotype.layout = request.data.get('layout')
        update_phenotype.type = request.data.get('type')
        update_phenotype.validation = request.data.get('validation')
        update_phenotype.valid_event_data_range_start = request.data.get('valid_event_data_range_start')
        update_phenotype.valid_event_data_range_end = request.data.get('valid_event_data_range_end')
        update_phenotype.sex = request.data.get('sex')
        update_phenotype.status = request.data.get('status')
        update_phenotype.hdr_created_date = request.data.get('hdr_created_date')
        update_phenotype.hdr_modified_date = request.data.get('hdr_modified_date')
        update_phenotype.publications = request.data.get('publications')
        update_phenotype.publication_doi = request.data.get('publication_doi')
        update_phenotype.publication_link = request.data.get('publication_link')
        update_phenotype.secondary_publication_links = request.data.get('secondary_publication_links')
        #update_phenotype.source_reference = request.data.get('source_reference') # With data_sources I don't think this is needed
        update_phenotype.citation_requirements = request.data.get('citation_requirements')
        update_phenotype.concept_informations = request.data.get('concept_informations')
        
        update_phenotype.updated_by = request.user        
        update_phenotype.modified = datetime.now() 
        
        # concepts
        concept_ids_list = request.data.get('concept_informations')
        if concept_ids_list is None or not isinstance(concept_ids_list, list):
            errors_dict['concept_informations'] = 'concept_informations must have a valid concept ids list'
        else:
            if len(concept_ids_list) == 0:
                errors_dict['concept_informations'] = 'concept_informations must have a valid non-empty concept ids list'
            else:
                if not chkListIsAllIntegers(concept_ids_list):
                    errors_dict['concept_informations'] = 'concept_informations must have a valid concept ids list'
                else: 
                    if len(set(concept_ids_list)) != len(concept_ids_list):
                        errors_dict['concept_informations'] = 'concept_informations must have a unique concept ids list'
                    else:
                        permittedConcepts = get_list_of_visible_concept_ids(
                                                                            get_visible_live_or_published_concept_versions(request , exclude_deleted = True)
                                                                            , return_id_or_history_id="id")
                        if not (set(concept_ids_list).issubset(set(permittedConcepts))):
                            errors_dict['concept_informations'] = 'invalid concept_informations ids list, all concept ids must be valid and accessible by user'
                        else:
                            concept_informations = convert_concept_ids_to_WSjson(concept_ids_list , no_attributes=True)
                            update_phenotype.concept_informations = concept_informations
                            update_phenotype.concept_version = getWSConceptsHistoryIDs(concept_informations, concept_ids_list = concept_ids_list)

        """data_sources = request.data.get('data_sources')
        if data_sources is None:
          update_phenotype.data_sources = None
        elif not isinstance(data_sources, list):
          errors_dict['data_sources'] = 'data_sources must be a valid list of data_source ids'
        else:
          if len(data_sources) == 0:
            errors_dict['data_sources'] = 'data_sources must be a valid non-empty list of data_source ids'
          else:
            if len(set(data_sources)) != len(data_sources):
              errors_dict['data_sources'] = 'data_sources must be a unique list of data_source ids'
            else:
              known_sources = set(get_visible_data_sources(request.user).exclude(is_deleted=True).values_list('id', flat=True))
              if not set(data_sources).issubset(known_sources):
                errors_dict['data_sources'] = 'Invalid data_sources ids listed, all data_source ids must be valid and accessible by the user'
              else:
                update_phenotype.data_sources = data_sources"""

        """clinical_terminologies = request.data.get('clinical_terminologies')
        if clinical_terminologies is None:
          update_phenotype.clinical_terminologies = None
        elif not isinstance(clinical_terminologies, list):
          errors_dict['clinical_terminologies'] = 'clinical_terminologies must be a valid list of clinical_terminology ids'
        else:
          if len(clinical_terminologies) == 0:
            errors_dict['clinical_terminologies'] = 'clinical_terminologies must be a valid non-empty list of clinical_terminology ids'
          else:
            if len(set(clinical_terminologies)) != len(clinical_terminologies):
              errors_dict['clinical_terminologies'] = 'clinical_terminologies must be a unique list of clinical_terminology ids'
            else:
              known_sources = set(get_visible_clinical_terminologies(request.user).exclude(is_deleted=True).values_list('id', flat=True))
              if not set(clinical_terminologies).issubset(known_sources):
                errors_dict['clinical_terminologies'] = 'Invalid clinical_terminologies ids listed, all clinical_terminology ids must be valid and accessible by the user'
              else:
                update_phenotype.clinical_terminologies = clinical_terminologies"""

        #  group id 
        is_valid_data, err, ret_value = chk_group(request.data.get('group') , user_groups)
        if is_valid_data:
            group_id = ret_value
            if group_id is None or group_id == "0":
                update_phenotype.group_id = None
                update_phenotype.group_access = 1
            else:
                update_phenotype.group_id = group_id
                is_valid_data, err, ret_value = chk_group_access(request.data.get('group_access'))
                if is_valid_data:
                    update_phenotype.group_access = ret_value
                else:
                    errors_dict['group_access'] = err
        else:
            errors_dict['group'] = err
      
        # handle world-access
        is_valid_data, err, ret_value = chk_world_access(request.data.get('world_access'))
        if is_valid_data:
            update_phenotype.world_access = ret_value
        else:
            errors_dict['world_access'] = err        

        # handling tags  
        tags = request.data.get('tags')
        is_valid_data, err, ret_value = chk_tags(request.data.get('tags'))
        if is_valid_data:
            tags = ret_value
        else:
            errors_dict['tags'] = err  

        # Validation
        errors_pt = {}
        if bool(errors_dict):
            is_valid = False
            
        is_valid_pt = True
        is_valid_pt, errors_pt = isValidPhenotype(request, update_phenotype)
        if not is_valid or not is_valid_pt:        
            errors_dict.update(errors_pt)
            return Response(
              data = errors_dict, 
              content_type="json", 
              status=status.HTTP_406_NOT_ACCEPTABLE
            )
        else:
            tag_ids = tags
            new_tag_list = []

            if tag_ids:
                new_tag_list = [int(i) for i in tag_ids]

            old_tag_list = list(PhenotypeTagMap.objects.filter(phenotype=update_phenotype).values_list('tag', flat=True))
            tag_ids_to_add = list(set(new_tag_list) - set(old_tag_list))
            tag_ids_to_remove = list(set(old_tag_list) - set(new_tag_list))

            for tag_id_to_add in tag_ids_to_add:
                PhenotypeTagMap.objects.get_or_create(phenotype=update_phenotype, tag=Tag.objects.get(id=tag_id_to_add), created_by=request.user)

            for tag_id_to_remove in tag_ids_to_remove:
                tag_to_remove = PhenotypeTagMap.objects.filter(phenotype=update_phenotype, tag=Tag.objects.get(id=tag_id_to_remove))
                tag_to_remove.delete()
                         
            update_phenotype.changeReason = "Updated from API"
            update_phenotype.save()   
            data = {
              'message': 'Phenotype updated successfully',
              'id': update_phenotype.pk
            }
            return Response(
              data = data, 
              content_type="text/json-comment-filtered", 
              status=status.HTTP_201_CREATED
            )

#--------------------------------------------------------------------------  
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def export_published_phenotype_codes(request, pk, phenotype_history_id):
    '''
        Return the unique set of codes and descriptions for the specified
        phenotype (pk),
        for a specific historical phenotype version (phenotype_history_id).
    '''

    if not Phenotype.objects.filter(id=pk).exists():            
        raise PermissionDenied


    if not Phenotype.history.filter(id=pk, history_id=phenotype_history_id).exists():
        raise PermissionDenied

 
    is_published = PublishedPhenotype.objects.filter(phenotype_id=pk, phenotype_history_id=phenotype_history_id).exists()
    # check if the phenotype version is published
    if not is_published: 
        raise PermissionDenied 
    
    #----------------------------------------------------------------------
    if request.method == 'GET':
        rows_to_return = get_phenotype_conceptcodesByVersion(request, pk, phenotype_history_id)
        return Response(rows_to_return, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------    
@api_view(['GET'])
def export_phenotype_codes_byVersionID(request, pk, phenotype_history_id):
    '''
        Return the unique set of codes and descriptions for the specified
        phenotype (pk),
        for a specific historical phenotype version (phenotype_history_id).
    '''
    # Require that the user has access to the base phenotype.
    # validate access for login site
    validate_access_to_view(request.user, Phenotype, pk, set_history_id=phenotype_history_id)

    #----------------------------------------------------------------------
        
    current_phenotype = Phenotype.objects.get(pk=pk)

    user_can_export = (allowed_to_view_children(request.user, Phenotype, pk, set_history_id=phenotype_history_id)
                        and
                        chk_deleted_children(request.user, Phenotype, pk, returnErrors = False, set_history_id=phenotype_history_id)
                        and 
                        not current_phenotype.is_deleted 
                      )

        
    if not user_can_export:
        raise PermissionDenied    
    #----------------------------------------------------------------------


    if request.method == 'GET':
        rows_to_return = get_phenotype_conceptcodesByVersion(request, pk, phenotype_history_id)
        return Response(rows_to_return, status=status.HTTP_200_OK)


##################################################################################
# search my phenotypes / published ones

#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([]) 
def published_phenotypes(request):
    return  getPhenotypes(request, is_authenticated_user=False)
    
#--------------------------------------------------------------------------
@api_view(['GET'])
def myPhenotypes(request):
    '''
        Get the API output for the list of my phenotypes.
    '''
    return  getPhenotypes(request, is_authenticated_user=True)
    
#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([]) 
#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([]) 
def getPhenotypes(request, is_authenticated_user=True):   
    search = request.query_params.get('search', '')
    phenotype_id = request.query_params.get('id', None)
    tag_ids = request.query_params.get('tag_ids', '')
    owner = request.query_params.get('owner_username', '')
    show_only_my_phenotypes = request.query_params.get('show_only_my_phenotypes', "0")
    show_deleted_phenotypes = request.query_params.get('show_deleted_phenotypes', "0")
    show_only_validated_phenotypes = request.query_params.get('show_only_validated_phenotypes', "0")
    phenotype_brand = request.query_params.get('brand', "")
    author = request.query_params.get('author', '')
    do_not_show_versions = request.query_params.get('do_not_show_versions', "0")
    expand_published_versions = request.query_params.get('expand_published_versions', "1")
    show_live_and_or_published_ver = request.query_params.get('show_live_and_or_published_ver', "3")      # 1= live only, 2= published only, 3= live+published
        
    search_tag_list = []
    tags = []
    
    filter_cond = " 1=1 "
    exclude_deleted = True
    get_live_and_or_published_ver = 3   # 1= live only, 2= published only, 3= live+published
    show_top_version_only = False
    
    if tag_ids:
        # split tag ids into list
        search_tag_list = [int(i) for i in tag_ids.split(",")]
        tags = Tag.objects.filter(id__in=search_tag_list)
        
    # check if it is the public site or not
    if is_authenticated_user:
        # ensure that user is only allowed to view/edit the relevant phenotypes
           
        get_live_and_or_published_ver = 3
        # show only phenotypes created by the current user
        if show_only_my_phenotypes == "1":
            filter_cond += " AND owner_id=" + str(request.user.id)
    
        # if show deleted phenotypes is 1 then show deleted phenotypes
        if show_deleted_phenotypes != "1":
            exclude_deleted = True
        else:
            exclude_deleted = False    
        
        if show_live_and_or_published_ver in ["1", "2", "3"]:
            get_live_and_or_published_ver = int(show_live_and_or_published_ver)   #    2= published only
        else:
            return Response([], status=status.HTTP_200_OK)
      
    else:
        # show published phenotypes
        get_live_and_or_published_ver = 2   #    2= published only
        #show_top_version_only = False
        
        if PublishedPhenotype.objects.all().count() == 0:
            return Response([], status=status.HTTP_200_OK)

    
    if expand_published_versions == "0":
        show_top_version_only = True
        
    

    if phenotype_id is not None:
        if phenotype_id != '':
            filter_cond += " AND id=" + phenotype_id
            
    if owner is not None:
        if owner !='':
            if User.objects.filter(username__iexact = owner.strip()).exists():
                owner_id = User.objects.get(username__iexact = owner.strip()).id
                filter_cond += " AND owner_id=" + str(owner_id)
            else:
                # username not found
                filter_cond += " AND owner_id= -1 "


    # if show_only_validated_phenotypes is 1 then show only phenotypes with validation_performed=True
    if show_only_validated_phenotypes == "1":
        filter_cond += " AND COALESCE(validation_performed, FALSE) IS TRUE "

    # show phenotypes for a specific brand
    if phenotype_brand != "":
        if Brand.objects.all().filter(name__iexact = phenotype_brand.strip()).exists():
            current_brand = Brand.objects.all().filter(name__iexact = phenotype_brand.strip())
            group_list = list(current_brand.values_list('groups', flat=True))
            filter_cond += " AND group_id IN("+ ', '.join(map(str, group_list)) +") "
        else:
            # brand name not found
            filter_cond += " AND group_id IN(-1) "
       
    phenotypes_srch = get_visible_live_or_published_phenotype_versions(request
                                                , get_live_and_or_published_ver = get_live_and_or_published_ver 
                                                , searchByName = search
                                                , author = author
                                                , exclude_deleted = exclude_deleted
                                                , filter_cond = filter_cond
                                                , show_top_version_only = show_top_version_only
                                                )
    
    
    # apply tags
    # I don't like this way :)
    phenotype_indx_to_exclude = []
    if tag_ids:
        for indx in range(len(phenotypes_srch)):  
            phenotype = phenotypes_srch[indx]
            phenotype['indx'] = indx
            phenotype_tags_history = getHistoryTags(phenotype['id'], phenotype['history_date'])
            if phenotype_tags_history:
                phenotype_tag_list = [i['tag_id'] for i in phenotype_tags_history if 'tag_id' in i]
                if not any(t in set(search_tag_list) for t in set(phenotype_tag_list)):
                    phenotype_indx_to_exclude.append(indx)
                else:
                    pass        
            else:
                phenotype_indx_to_exclude.append(indx)  
        
    if phenotype_indx_to_exclude:      
        phenotypes = [i for i in phenotypes_srch if (i['indx'] not in phenotype_indx_to_exclude)]
    else:
        phenotypes = phenotypes_srch 
     

    rows_to_return = []
    titles = ['phenotype_id', 'version_id'
            , 'UUID', 'phenotype_name'
            , 'type'
            , 'author', 'owner'
            , 'created_by', 'created_date'  
            , 'modified_by', 'modified_date'  
            , 'is_deleted', 'deleted_by', 'deleted_date'
            , 'is_published'
            ]
    if do_not_show_versions != "1":
        titles += ['versions']
    

    for c in phenotypes:
        ret = [
                c['id'],  
                c['history_id'],  
                c['phenotype_id'], #UUID
                c['name'].encode('ascii', 'ignore').decode('ascii'),
                c['type'],           
                c['author'],
                c['owner_name'],
                
                c['created_by_username'],
                c['created'],
            ]

        if (c['updated_by_id']):
            ret += [c['modified_by_username']]
        else:
            ret += [None]
            
        ret += [
                c['modified'],  
                
                c['is_deleted'],  
            ]
        
        if (c['is_deleted'] == True):
            ret += [c['deleted_by_username']]
        else:
            ret += [None]
        
        ret += [c['deleted'], c['published']]
        
        if do_not_show_versions != "1":
            ret += [get_visible_versions_list(request, Phenotype, c['id'], is_authenticated_user)]
        
        rows_to_return.append(ordr(zip(titles,  ret )))
                                   
    return Response(rows_to_return, status=status.HTTP_200_OK)                                   


                                               
# show phenotype detail
#============================================================= 
@api_view(['GET'])
def myPhenotype_detail(request, pk, phenotype_history_id=None):
    ''' 
        Display the detail of a phenotype at a point in time.
    '''
    
    if Phenotype.objects.filter(id=pk).count() == 0: 
        raise Http404
    
    if phenotype_history_id is not None:
        phenotype_ver = Phenotype.history.filter(id=pk, history_id=phenotype_history_id) 
        if phenotype_ver.count() == 0: raise Http404
        
        
    # validate access phenotype
    if not allowed_to_view(request.user, Phenotype, pk, set_history_id=phenotype_history_id):
        raise PermissionDenied
    
    # we can remove this check as in phenotype-detail
    #---------------------------------------------------------
    # validate access to child phenotypes 
    if not (allowed_to_view_children(request.user, Phenotype, pk, set_history_id=phenotype_history_id)
            and
            chk_deleted_children(request.user, Phenotype, pk, returnErrors = False, set_history_id=phenotype_history_id)
           ):
        raise PermissionDenied
    #---------------------------------------------------------
            
    if phenotype_history_id is None:
        # get the latest version
        phenotype_history_id = Phenotype.objects.get(pk=pk).history.latest().history_id 
        
                    
    return getPhenotypeDetail(request, pk, phenotype_history_id)
    
#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([]) 
def myPhenotype_detail_PUBLIC(request, pk, phenotype_history_id=None):
    ''' 
        Display the detail of a published phenotype at a point in time.
    '''
    
    if Phenotype.objects.filter(id=pk).count() == 0: 
        raise Http404
    
    if phenotype_history_id is not None:
        phenotype_ver = Phenotype.history.filter(id=pk, history_id=phenotype_history_id) 
        if phenotype_ver.count() == 0: raise Http404
        
            
    if phenotype_history_id is None:
        # get the latest version
        phenotype_history_id = Phenotype.objects.get(pk=pk).history.latest().history_id 
        
    is_published = checkIfPublished(Phenotype, pk, phenotype_history_id)
    # check if the phenotype version is published
    if not is_published: 
        raise PermissionDenied 
                    
    return getPhenotypeDetail(request, pk, phenotype_history_id)
    
        
#--------------------------------------------------------------------------
def getPhenotypeDetail(request, pk, phenotype_history_id=None):
    
    phenotype = getHistoryPhenotype(phenotype_history_id)
    # The history phenotype contains the owner_id, to provide the owner name, we
    # need to access the user object with that ID and add that to the phenotype.
    phenotype['owner'] = None
    if phenotype['owner_id'] is not None:
        phenotype['owner'] = User.objects.get(pk=phenotype['owner_id']).username

    phenotype['group'] = None
    if phenotype['group_id'] is not None: 
        phenotype['group'] = Group.objects.get(pk=phenotype['group_id']).name


    phenotype_history_date = phenotype['history_date']
    #--------------
        
    concept_id_list = [x['concept_id'] for x in json.loads(phenotype['concept_informations'])] 
    concept_hisoryid_list = [x['concept_version_id'] for x in json.loads(phenotype['concept_informations'])] 
    concepts = list(Concept.history.filter(id__in=concept_id_list, history_id__in=concept_hisoryid_list).values('id', 'history_id', 'name', 'group'))
    
    CodingSystem_ids = Concept.history.filter(id__in=concept_id_list, history_id__in=concept_hisoryid_list).order_by().values('coding_system_id').distinct()
    clinicalTerminologies = list(CodingSystem.objects.filter(pk__in=list(CodingSystem_ids.values_list('coding_system_id', flat=True))))
    #--------------
    
    tags =  []
    tags_comp = getHistoryTags(pk, phenotype_history_date)
    if tags_comp:
        tag_list = [i['tag_id'] for i in tags_comp if 'tag_id' in i]
        tags = list(Tag.objects.filter(pk__in=tag_list).values('description', 'id'))
    

    rows_to_return = []
    titles = [
            'phenotype_id'
            , 'version_id'
            , 'UUID'
            , 'phenotype_name'
            , 'type'
            , 'tags'
            , 'author'
            #, 'entry_date'
            , 'clinical_terminologies'
            #, 'description'            
            
            , 'created_by', 'created_date'  
            , 'modified_by', 'modified_date'  
            
            , 'validation_performed' 
            #, 'validation_description'
            , 'publication_doi'
            , 'publication_link'
            #, 'secondary_publication_links'
            , 'source_reference'
            , 'citation_requirements'
           
            , 'implementation'
            , 'publications'
            
            , 'owner', 'owner_access'
            , 'group', 'group_access'
            , 'world_access'
            
            , 'is_deleted'  # may come from phenotype live version / or history
            # , 'deleted_by', 'deleted_date' # no need here
            
            , 'concepts'
            ]
    
    ret = [
            phenotype['id'],
            phenotype['history_id'],
            phenotype['phenotype_id'],  #UUID
            phenotype['name'].encode('ascii', 'ignore').decode('ascii'),
            phenotype['type'],
            
            tags,
            phenotype['author'],
            #phenotype['entry_date'],
            clinicalTerminologies,
            #phenotype['description'],
            
            
            phenotype['created_by_username'],
            phenotype['created'],   
            phenotype['modified_by_username'],
            phenotype['modified'],

            phenotype['validation_performed'],
            #phenotype['validation_description'],
            phenotype['publication_doi'],
            phenotype['publication_link'],
            #phenotype['secondary_publication_links'],
            phenotype['source_reference'],
            phenotype['citation_requirements'],
            
            phenotype['implementation'],
            phenotype['secondary_publication_links'],
            
            phenotype['owner'] ,
            dict(Permissions.PERMISSION_CHOICES)[phenotype['owner_access']],
            phenotype['group'],
            dict(Permissions.PERMISSION_CHOICES)[phenotype['group_access']],
            dict(Permissions.PERMISSION_CHOICES)[phenotype['world_access']],
        ]
    
    # may come from phenotype live version / or history    
    if (phenotype['is_deleted'] == True or Phenotype.objects.get(pk=pk).is_deleted==True):
        ret += [True]
    else:
        ret += [None]
            

    # concepts
    com_titles = ['name', 'concept_id', 'concept_version_id'
                , 'codes'
                ]
    
    ret_concepts = []
    for c in concepts:
        ret_codes = []
        ret_codes = getGroupOfCodesByConceptId_HISTORICAL(c['id'], c['history_id'])
        
        
#         for code in codes:
#             ret_codes.append(ordr(zip(
#                                         ['code', 'description']
#                                         ,  [code['code'], code['description']] 
#                                     )
#                                 )
#                             )
            
        ret_comp_data = [
                            c['name'], 
                            c['id'],
                            c['history_id'],
                            ret_codes
                        ]
        ret_concepts.append(ordr(zip(com_titles,  ret_comp_data )))


    #ret += [concepts]
    ret += [ret_concepts]
    
    
    rows_to_return.append(ordr(zip(titles,  ret )))
                                   
    return Response(rows_to_return, status=status.HTTP_200_OK)                
    
    
    
    
    

    

