from datetime import datetime
from django.db.models import Q
from django.db import connection
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import BadRequest, PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.reverse import reverse

import re
import json
import logging

from clinicalcode.entity_utils import permission_utils
from clinicalcode.models.Tag import Tag
from clinicalcode.models.Concept import Concept
from clinicalcode.models.Phenotype import Phenotype
from clinicalcode.models.WorkingSet import WorkingSet
from clinicalcode.models.GenericEntity import GenericEntity
from clinicalcode.models.PublishedPhenotype import PublishedPhenotype

logger = logging.getLogger(__name__)

#### Dynamic Template  ####
def sort_pk_list(a, b):
    pk1 = int(a.replace('PH', ''))
    pk2 = int(b.replace('PH', ''))

    if pk1 > pk2:
        return 1
    elif pk1 < pk2:
        return -1
    return 0

def try_parse_doi(publications):
    import re
    pattern = re.compile(r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*\/(?:(?![\"&\'<>])\S)+)\b')

    output = [ ]
    for publication in publications:
        if publication is None or len(str(publication).strip()) < 1:
            continue

        doi = pattern.findall(publication)
        output.append({
            'details': publication,
            'doi': doi[0] if len(doi) > 0 else None
        })
    
    return output

def compute_related_brands(pheno, default=''):
    collections = pheno.collections
    if not isinstance(collections, list):
        return default
    
    related_brands = set([])
    for collection_ids in collections:
        collection = Tag.objects.filter(id=collection_ids)
        if not collection.exists():
            continue

        brand = collection.first().collection_brand
        if brand is None:
            continue
        related_brands.add(brand.id)
    
    related_brands = ','.join([str(x) for x in list(related_brands)])
    return "brands='{%s}' " % related_brands

@login_required
def admin_mig_concepts_dt(request):
    '''
        Approximates ownership of a Concept given it's first appearance
        in a phenotype

        i.e.
            for concept in concepts:
                concept.phenotype_owner = earliest_record_as_child_of_phenotype(concept.id)

    '''
    if settings.CLL_READ_ONLY: 
        raise PermissionDenied
    
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if not permission_utils.is_member(request.user, 'system developers'):
        raise PermissionDenied

    # get
    if request.method == 'GET':
        return render(
            request,
            'clinicalcode/adminTemp/admin_mig_phenotypes_dt.html', 
            {
                'url': reverse('admin_mig_concepts_dt'),
                'action_title': 'Migrate Concepts',
                'hide_phenotype_options': True,
            }
        )

    # post
    if request.method != 'POST':
        raise BadRequest('Invalid')

    with connection.cursor() as cursor:
        sql = '''
        with
            split_concepts as (
                select phenotype.id as phenotype_id, 
                    concept ->> 'concept_id' as concept_id,
                    created
                from public.clinicalcode_phenotype as phenotype,
                    json_array_elements(phenotype.concept_informations :: json) as concept
            ),
            ranked_concepts as (
                select phenotype_id, concept_id,
                    rank() over(
                        partition by concept_id
                        order by created
                    ) ranking
                from split_concepts
            )

        update public.clinicalcode_concept as trg
           set phenotype_owner_id = src.phenotype_id
          from ranked_concepts as src
         where trg.id = src.concept_id::int;
        
        update public.clinicalcode_historicalconcept as trg
           set phenotype_owner_id = src.phenotype_owner_id
          from public.clinicalcode_concept as src
         where trg.id = src.id;
        '''
        cursor.execute(sql)

    return render(
        request,
        'clinicalcode/adminTemp/admin_mig_phenotypes_dt.html',
        {
            'pk': -10,
            'rowsAffected' : { '1': 'ALL'},
            'action_title': 'Migrate Concepts',
            'hide_phenotype_options': True,
        }
    )

@login_required
def admin_mig_phenotypes_dt(request):
    # for admin(developers) to migrate phenotypes into dynamic template
   
    if settings.CLL_READ_ONLY: 
        raise PermissionDenied
    
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if not permission_utils.is_member(request.user, 'system developers'):
        raise PermissionDenied
    
    if request.method == 'GET':
        if not settings.CLL_READ_ONLY: 
            return render(request, 'clinicalcode/adminTemp/admin_mig_phenotypes_dt.html', 
                          {'url': reverse('admin_mig_phenotypes_dt'),
                           'action_title': 'Migrate Phenotypes'
                        })
    
    elif request.method == 'POST':
        if not settings.CLL_READ_ONLY: 
            code = request.POST.get('code')
            if code.strip() != "6)r&9hpr_a0_4g(xan5p@=kaz2q_cd(v5n^!#ru*_(+d)#_0-i":
                raise PermissionDenied
    
            phenotype_ids = request.POST.get('phenotype_ids')
            phenotype_ids = phenotype_ids.strip().upper()

            rowsAffected = {} 
            
            if phenotype_ids:
                if phenotype_ids == 'ALL': # mig ALL                    
                    with connection.cursor() as cursor:
                        sql = "truncate table clinicalcode_historicalgenericentity restart identity; "
                        cursor.execute(sql)
                        sql2 = "truncate table clinicalcode_historicalpublishedgenericentity restart identity; "
                        cursor.execute(sql2)   
                        sql3 = """
                        DO
                        $do$
                        declare CONSTRAINT_NAME text:= (
                            select quote_ident(conname)
                            from pg_constraint
                            where conrelid = 'public.clinicalcode_concept'::regclass
                            and confrelid = 'public.clinicalcode_genericentity'::regclass
                            limit 1
                        );

                        begin
                            execute 'alter table public.clinicalcode_concept drop constraint if exists ' || CONSTRAINT_NAME;

                            execute 'update public.clinicalcode_concept set phenotype_owner_id = NULL';

                            execute 'truncate table public.clinicalcode_genericentity, public.clinicalcode_publishedgenericentity restart identity';

                            execute 'alter table public.clinicalcode_concept
                                add constraint ' || CONSTRAINT_NAME || ' foreign key (phenotype_owner_id)
                                references public.clinicalcode_genericentity (id)';
                        end
                        $do$
                        """
                        cursor.execute(sql3)
                    
                    
                        mig_h_pheno = """
                        INSERT INTO clinicalcode_historicalgenericentity(
                            id, name, author, status, tags, collections, definition
                            , implementation, validation, citation_requirements
                            , template_data, template_id, template_version, internal_comments
                            , created, updated, is_deleted, deleted, owner_access, group_access, world_access
                            , history_id, history_date, history_change_reason, history_type, history_user_id
                            , created_by_id, deleted_by_id, group_id, owner_id, updated_by_id
                            )
                        SELECT id, name, author, 2 status, tags, collections, description definition
                            , implementation, validation, citation_requirements
                            , '{}' template_data, 1 template_id, 1 template_version, '' internal_comments
                            , created, modified updated, is_deleted, deleted, owner_access, group_access, world_access
                            , history_id, history_date, history_change_reason, history_type, history_user_id
                            , created_by_id, deleted_by_id, group_id, owner_id, updated_by_id
                        FROM clinicalcode_historicalphenotype;
                        """
                        cursor.execute(mig_h_pheno) 
                    
                        mig_pheno = """
                        INSERT INTO clinicalcode_genericentity(
                            id, name, author, status, tags, collections, definition
                            , implementation, validation, citation_requirements
                            , template_data, template_id, template_version, internal_comments
                            , created, updated, is_deleted, deleted, owner_access, group_access, world_access
                            , created_by_id, deleted_by_id, group_id, owner_id, updated_by_id
                            )
                        SELECT id, name, author, 2 status, tags, collections, description definition                       
                            , implementation, validation, citation_requirements
                            , '{}' template_data, 1 template_id, 1 template_version, '' internal_comments
                            , created, modified updated, is_deleted, deleted, owner_access, group_access, world_access
                            , created_by_id, deleted_by_id, group_id, owner_id, updated_by_id
                        FROM clinicalcode_phenotype;
                        """
                        cursor.execute(mig_pheno)
                    
                        mig_h_published_records = """
                        insert into clinicalcode_historicalpublishedgenericentity(
                            id, entity_id, entity_history_id, code_count
                            , moderator_id, approval_status
                            , created, created_by_id, modified, modified_by_id
                            , history_id, history_date, history_change_reason, history_type, history_user_id
                            )    
                        SELECT id, phenotype_id, phenotype_history_id, null code_count
                            , moderator_id, approval_status
                            , created, created_by_id, modified, modified_by_id
                            , history_id, history_date, history_change_reason, history_type, history_user_id
                            FROM clinicalcode_historicalpublishedphenotype
                            where phenotype_id like 'PH%';
                        """
                        cursor.execute(mig_h_published_records)
                    
                        mig_published_records = """
                        insert into clinicalcode_publishedgenericentity(
                            id, entity_id, entity_history_id, code_count
                            , moderator_id, approval_status
                            , created, created_by_id, modified, modified_by_id
                            )    
                        SELECT id, phenotype_id, phenotype_history_id, null code_count
                            , moderator_id, approval_status
                            , created, created_by_id, modified, modified_by_id
                            FROM clinicalcode_publishedphenotype
                            where phenotype_id like 'PH%';
                        """
                        cursor.execute(mig_published_records)                           
                    
                    ######################################
                    live_pheno = Phenotype.objects.all()

                    live_pheno_count = Phenotype.objects.extra(
                        select={
                            'true_id': '''CAST(SUBSTRING(id, 3, LENGTH(id)) AS INTEGER)'''
                        }
                    ).order_by('-true_id', 'id').first()
                    live_pheno_count = live_pheno_count.true_id

                    for p in live_pheno:
                        temp_data = get_custom_fields_key_value(p)
                        temp_data['version'] = 1
                        publication_items = try_parse_doi([i.replace("'", "''") for i in p.publications])
                        
                        ''' update publish status in live generic entity '''
                        publish_status_str = ""
                        approval_status = ""
                        p_latest_history_id =  p.history.latest().history_id
                        if PublishedPhenotype.objects.filter(phenotype_id=p.id, phenotype_history_id=p_latest_history_id).exists():
                            approval_status = str(PublishedPhenotype.objects.get(phenotype_id=p.id, phenotype_history_id=p_latest_history_id).approval_status)
                            publish_status_str = " , publish_status = " + approval_status + " "
                        
                        brand_status = compute_related_brands(p)
                        with connection.cursor() as cursor:
                            sql_p = """
                                    update clinicalcode_genericentity  
                                    set template_data = '"""+json.dumps(temp_data)+"""',
                                        publications= '"""+json.dumps(publication_items)+"""'
                                        """+publish_status_str+"""
                                        , """+brand_status+"""
                                    where id ='"""+p.id+"""' ;
                                    """
                            cursor.execute(sql_p)

                            sql_p = """
                                    update clinicalcode_historicalgenericentity  
                                    set """+brand_status+"""
                                    where id ='"""+p.id+"""';
                                    """
                            cursor.execute(sql_p)
                    
                    with connection.cursor() as cursor:
                        sql_entity_count = "update clinicalcode_entityclass set entity_count ="+str(live_pheno_count)+" where id = 1;"
                        cursor.execute(sql_entity_count)

                    historical_pheno = Phenotype.history.filter(~Q(id='x'))
                    for p in historical_pheno:
                        temp_data = get_custom_fields_key_value(p)
                        temp_data['version'] = 1
                        publication_items = try_parse_doi([i.replace("'", "''") for i in p.publications])
                        with connection.cursor() as cursor:
                            sql_p = """ update  clinicalcode_historicalgenericentity  
                                    set template_data = '"""+json.dumps(temp_data)+"""'
                                        , publications= '"""+json.dumps(publication_items)+"""'
                                    where id ='"""+p.id+"""' and history_id='"""+str(p.history_id)+"""';
                                    """
                            cursor.execute(sql_p)
                            
                    ''' update publish status in historical generic entity '''
                    with connection.cursor() as cursor:
                        sql_publish_status = """
                                                UPDATE public.clinicalcode_historicalgenericentity AS hg
                                                SET publish_status = p.approval_status
                                                FROM public.clinicalcode_publishedgenericentity AS p
                                                WHERE hg.id = p.entity_id and hg.history_id = p.entity_history_id ;

                                                UPDATE public.clinicalcode_historicalgenericentity AS hg
                                                SET publish_status = p.approval_status
                                                FROM public.clinicalcode_publishedgenericentity AS p
                                                WHERE hg.id = p.entity_id and hg.history_id = p.entity_history_id ;
                                            """
                        cursor.execute(sql_publish_status)
                        

                    with connection.cursor() as cursor:
                        cursor.execute("""SELECT SETVAL(
                            pg_get_serial_sequence('clinicalcode_historicalgenericentity', 'history_id'),
                            (SELECT MAX(history_id) FROM public.clinicalcode_historicalgenericentity)
                        );""")
                        
                    with connection.cursor() as cursor:
                        cursor.execute("""SELECT SETVAL(
                            pg_get_serial_sequence('clinicalcode_historicalpublishedgenericentity', 'history_id'),
                            (SELECT MAX(history_id) FROM public.clinicalcode_historicalpublishedgenericentity)
                        );""")

                    with connection.cursor() as cursor:
                        cursor.execute("""SELECT setval('clinicalcode_publishedgenericentity_id_seq',
                                       (SELECT MAX(id) FROM public.clinicalcode_publishedgenericentity)+1);""")


                    ######################################
                    rowsAffected[1] = "phenotypes migrated."
            else:
                rowsAffected[-1] = "Phenotype IDs NOT correct"
    
            return render(
                request,
                'clinicalcode/adminTemp/admin_mig_phenotypes_dt.html',
                {   'pk': -10,
                    'rowsAffected' : rowsAffected,
                    'action_title': 'Migrate Phenotypes'
                }
            )

@login_required
def admin_fix_breathe_dt(request):
    if settings.CLL_READ_ONLY: 
        raise PermissionDenied
    
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if not permission_utils.is_member(request.user, 'system developers'):
        raise PermissionDenied

    # get
    if request.method == 'GET':
        return render(
            request,
            'clinicalcode/adminTemp/admin_mig_phenotypes_dt.html', 
            {
                'url': reverse('admin_fix_breathe_dt'),
                'action_title': 'Fix Breathe Phenotypes',
                'hide_phenotype_options': True,
            }
        )

    # post
    if request.method != 'POST':
        raise BadRequest('Invalid')

    with connection.cursor() as cursor:
        sql = """
        UPDATE public.clinicalcode_genericentity
        SET validation =CONCAT(validation, '21')
        WHERE name LIKE 'Acute bronchitis%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_genericentity
        SET validation =CONCAT(validation, '7')
        WHERE name LIKE 'Asthma%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_genericentity
        SET validation =CONCAT(validation, '%.')
        WHERE name LIKE 'Chronic obstructive%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_genericentity
        SET validation =CONCAT(validation, 'a.')
        WHERE name LIKE 'Empyema%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_genericentity
        SET validation =CONCAT(validation, 's.')
        WHERE name LIKE 'Influenza infection%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_genericentity
        SET validation =CONCAT(validation, 'hs')
        WHERE name LIKE 'Pertussis%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_genericentity
        SET validation ='The definition of pneumonia has not been validated'
        WHERE name LIKE 'Pneumonia%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;
        """
        cursor.execute(sql)
        print(cursor.rowcount, "record(s) affected")

    with connection.cursor() as cursor:

        historical = """
        UPDATE public.clinicalcode_historicalgenericentity
        SET validation =CONCAT(validation, '21')
        WHERE name LIKE 'Acute bronchitis%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_historicalgenericentity
        SET validation =CONCAT(validation, '7')
        WHERE name LIKE 'Asthma%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_historicalgenericentity
        SET validation =CONCAT(validation, '%.')
        WHERE name LIKE 'Chronic obstructive%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_historicalgenericentity
        SET validation =CONCAT(validation, 'a.')
        WHERE name LIKE 'Empyema%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_historicalgenericentity
        SET validation =CONCAT(validation, 's.')
        WHERE name LIKE 'Influenza infection%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_historicalgenericentity
        SET validation =CONCAT(validation, 'hs')
        WHERE name LIKE 'Pertussis%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_historicalgenericentity
        SET validation ='The definition of pneumonia has not been validated'
        WHERE name LIKE 'Pneumonia%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;

        UPDATE public.clinicalcode_historicalgenericentity
        SET validation =CONCAT(validation, 'hs')
        WHERE name LIKE 'Rhinitis%'
        AND template_data ->> 'phenotype_uuid' LIKE 'excel-breathe%'
        AND validation IS NOT NULL;
        """
        cursor.execute(historical)

        return render(
            request,
            'clinicalcode/adminTemp/admin_mig_phenotypes_dt.html',
            {   'pk': -10,
                'action_title': 'Fix Breathe',
            }
        )

def get_serial_id():
    count_all = GenericEntity.objects.count()
    if count_all:
        count_all += 1
    else:
        count_all = 1
        
    return count_all

def get_agreement_date(phenotype):
    if phenotype.hdr_modified_date:
        return phenotype.hdr_modified_date
    else:
        return phenotype.hdr_created_date

def get_sex(phenotype):
    sex = str(phenotype.sex).lower().strip()
    if sex == 'male':
        return 1
    elif sex == 'female':
        return 2
    else:
        return 3

def get_type(phenotype):
    type = str(phenotype.type).lower().strip()
    if type == "biomarker":
        return 1
    elif type == "disease or syndrome":
        return 2
    elif type == "drug":
        return 3
    elif type == "lifestyle risk factor":
        return 4
    elif type == "musculoskeletal":
        return 5
    elif type == "surgical procedure":
        return 6    
    else:
        return -1

def get_custom_fields(phenotype):
    ret_data = {}
    
    ret_data['type'] = str(get_type(phenotype))
    ret_data['concept_information'] = phenotype.concept_informations
    ret_data['coding_system'] = phenotype.clinical_terminologies
    ret_data['data_sources'] = phenotype.data_sources
    ret_data['phenoflowid'] = phenotype.phenoflowid    
    ret_data['agreement_date'] = get_agreement_date(phenotype)
    ret_data['phenotype_uuid'] = phenotype.phenotype_uuid
    ret_data['event_date_range'] = phenotype.valid_event_data_range
    ret_data['sex'] = str(get_sex(phenotype))
    ret_data['source_reference'] = phenotype.source_reference
    
    return ret_data
    
def get_custom_fields_key_value(phenotype):
    """
        return one dict of col_name/col_value pairs
    """
    
    return get_custom_fields(phenotype)
