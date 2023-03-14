from enum import Enum

class APPROVAL_STATUS(int, Enum):
    '''
        
    '''
    REQUESTED = 0
    PENDING   = 1
    APPROVED  = 2
    REJECTED  = 3

class GROUP_PERMISSIONS(int, Enum):
    '''
        
    '''
    NONE = 1
    VIEW = 2
    EDIT = 3

'''
    Entity render modifier(s)
        Used by entity_renderer as defaults
'''
DEFAULT_CARD = 'generic'
CARDS_DIRECTORY = 'components/search/cards'

'''
    Filter render modifier(s)
        Used by entity_renderer as defaults
'''
FILTER_SERVICE_FILE = 'js/clinicalcode/redesign/services/filterService.js'
FILTER_DIRECTORY = 'components/search/filters'
FILTER_COMPONENTS = {
    'int': 'checkbox',
    'enum': 'checkbox',
    'int_array': 'checkbox',
    'datetime': 'datepicker',
}

'''
    Threshold for layout count in single search pages (__gte)
'''
MIN_SINGLE_SEARCH = 1

'''
    Order by clauses for search
'''
ORDER_BY = {
    '1': {
        'name': 'Relevance',
        'clause': 'id'
    },
    '2': {
        'name': 'Created (Asc)',
        'clause': 'created'
    },
    '3': {
        'name': 'Created (Desc)',
        'clause': '-created'
    },
    '4': {
        'name': 'Updated (Asc)',
        'clause': 'updated'
    },
    '5': {
        'name': 'Updated (Desc)',
        'clause': '-updated'
    }
}

'''
    Page result limits for search
'''
PAGE_RESULTS_SIZE = {
    '1': 20,
    '2': 50,
    '3': 100
}

'''
    [!] Note: Will be moved to a table once tooling is finished, accessible through the 'base_template_version'

    Used to define:
        - Hashmap for values from sourced data
        - By filter to determine metadata-related filters
'''
metadata = {
    "template": {
        "title": "Entity Type",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "int",
            "mandatory": True,
            "computed": True,
            "source": {
                "table": "Template",
                "query": "id",
                "relative": "name"
            }
        },
        "search": {
            "filterable": True,
            "single_search_only": True,
        }
    },
    "name": {
        "title": "Name",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": True
        },
        "is_base_field": True
    },
    "definition": {
        "title": "Definition",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": False
        },
        "is_base_field": True
    },
    "implementation": {
        "title": "Implementation",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": False
        },
        "is_base_field": True
    },
    "publications": {
        "title": "Publications",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "string_array",
            "mandatory": False
        },
        "is_base_field": True
    },
    "validation": {
        "title": "Validation",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": False
        },
        "is_base_field": True
    },
    "citation_requirements": {
        "title": "Citation Requirements",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": False
        },
        "is_base_field": True
    },
    "created": {
        "title": "Date",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "datetime",
            "mandatory": True,
            "computed": True
        },
        "search": {
            "filterable": True
        },
        "is_base_field": True
    },
    "author": {
        "title": "Author",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": True
        },
        "is_base_field": True
    },
    "collections": {
        "title": "Collections",
        "field_type": "???",
        "active": True,
        "compute_statistics": True,
        "validation": {
            "type": "int_array",
            "mandatory": False,
            "source": {
                "table": "Tag",
                "query": "id",
                "relative": "description",
                "filter": {
                    "tag_type": 2
                }
            }
        },
        "search": {
            "filterable": True,
            "api": True
        },
        "is_base_field": True
    },
    "tags": {
        "title": "Tags",
        "field_type": "???",
        "active": True,
        "compute_statistics": True,
        "validation": {
            "type": "int_array",
            "mandatory": False,
            "source": {
                "table": "Tag",
                "query": "id",
                "relative": "description",
                "filter": {
                    "tag_type": 1
                }
            }
        },
        "search": {
            "filterable": True,
            "api": True
        },
        "is_base_field": True
    },
    "updated": {
        "title": "Updated",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "datetime",
            "mandatory": True
        },
        "is_base_field": True
    },
    "created_by": {
        "title": "Created By",
        "field_type": "???",
        "active": True,
        "requires_auth": True,
        "validation": {
            "type": "int", 
            "mandatory": True
        },
        "is_base_field": True
    },
    "updated_by": {
        "title": "Updated By",
        "field_type": "???",
        "active": True,
        "requires_auth": True,
        "validation": {
            "type": "int", 
            "mandatory": True
        },
        "is_base_field": True
    },
}



#-----------------------------------
metadataXX =  {
    "template": {
        "title": "Entity Type",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "int",
            "mandatory": True,
            "computed": True,
            "source": {
                "table": "Template",
                "query": "id",
                "relative": "name"
            }
        },
        "search": {
            "filterable": True,
            "single_search_only": True,
        }
    },
         "name": {
             "title": "Name",
             "active": True,
             "mandatory": True,
             "field_type": "string_inputbox",
             "side_menu": "home"
         },
         "author": {
             "title": "Author",
             "active": True,
             "mandatory": True,
             "field_type": "string_inputbox"
         },
         "collections": {
             "title": "Collections",
             "active": True,
             "mandatory": False,
             "field_type": "collections"
         },
         "tags": {
             "title": "Tags",
             "active": True,
             "mandatory": False,
             "field_type": "tags"
         },
         "definition": {
             "title": "Definition",
             "active": True,
             "mandatory": False,
             "field_type": "textarea_markdown",
             "side_menu": "Definition"
         },
         "implementation": {
             "title": "Implementation",
             "active": True,
             "mandatory": False,
             "field_type": "textarea_markdown",
             "side_menu": "Implementation"
         },
         "publications": {
             "title": "Publications",
             "active": True,
             "mandatory": False,
             "field_type": "string_list_of_inputboxes",
             "side_menu": "Publications"
         },
         "validation": {
             "title": "Validation",
             "active": True,
             "mandatory": False,
             "field_type": "textarea_markdown",
             "do_not_show_in_production": True,
             "side_menu": "Validation",
             "hide_if_empty": True
         },
         "citation_requirements": {
             "title": "Citation Requirements",
             "active": True,
             "mandatory": False,
             "field_type": "textarea",
             "hide_if_empty": True
         },
         "updated": {
        "title": "Updated",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "datetime",
            "mandatory": True
        },
        "is_base_field": True
    },
    "created_by": {
        "title": "Created By",
        "field_type": "???",
        "active": True,
        "requires_auth": True,
        "validation": {
            "type": "int", 
            "mandatory": True
        },
        "is_base_field": True
    },
    "updated_by": {
        "title": "Updated By",
        "field_type": "???",
        "active": True,
        "requires_auth": True,
        "validation": {
            "type": "int", 
            "mandatory": True
        },
        "is_base_field": True
    },
 }

FIELD_TYPES = {

    "int": {
        "data_type": "int",
        "input_type": "textinput"
    },
    "date": {
        "data_type": "date",
        "input_type": "date_picker"
    },
    "string_inputbox": {
        "data_type": "string",
        "input_type": "textinput",
        "max_length": 250
    },
    "string_inputbox_code": {
        "data_type": "string",
        "input_type": "textinput",
        "max_length": 250,
        "apply_code_style": True
    },
    "textarea": {
        "data_type": "string",
        "input_type": "textarea",
        "rows": 5
    },
    "textarea_markdown": {
        "data_type": "string",
        "input_type": "textarea",
        "rows": 5,
        "display": "markdown"
    },
    "string_list_of_inputboxes": {
        "data_type": "string",
        "input_type": "list_of_inputboxes",
        "max_length": 250
    },
    "string_list_of_inputboxes_markdown": {
        "data_type": "string",
        "input_type": "list_of_inputboxes",
        "max_length": 250,
        "display": "markdown"
    },

    "enum": {
        "data_type": "int",
        "input_type": "dropdown-list",
        "use_permitted_values": True
    },

    "enum_badge": {
        "data_type": "int",
        "input_type": "dropdown-list",
        "use_permitted_values": True,
        "apply_badge_style": True
    },

    "concept_information": {
        "system_defined": True,
        "description": "json of concept ids/ver used in phenotype (managed by code snippet)"
    },
    "coding_system": {
        "system_defined": True,
        "description": "list of coding system ids (calculated from phenotype concepts) (managed by code snippet)"
    },
    "tags": {
        "system_defined": True,
        "description": "list of tags ids (managed by code snippet)"
    },
    "collections": {
        "system_defined": True,
        "description": "list of collections ids (managed by code snippet)"
    },
    "data_sources": {
        "system_defined": True,
        "description": "list of data_sources ids (managed by code snippet)"
    },
    "phenoflowid": {
        "system_defined": True,
        "description": "URL for phenoflow (managed by code snippet)"
    }

}

#####################################


