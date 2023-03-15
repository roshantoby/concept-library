from enum import Enum
from django.contrib.auth.models import User

class ENTITY_STATUS(int, Enum):
    '''
        Status of an entity
    '''
    DRAFT = 1
    FINAL = 2

class APPROVAL_STATUS(int, Enum):
    '''
        Approval status of a published entity
    '''
    REQUESTED = 0
    PENDING   = 1
    APPROVED  = 2
    REJECTED  = 3

class GROUP_PERMISSIONS(int, Enum):
    '''
        Permission groups
    '''
    NONE = 1
    VIEW = 2
    EDIT = 3

class FORM_METHODS(str, Enum):
    '''
        Describes form method, i.e. to create or update an entity
        Used by both template and view to modify behaviour
    '''
    CREATE = 1
    UPDATE = 2

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
    Entity creation related defaults
'''
CREATE_WIZARD_ASIDE = 'components/create/aside.html'
CREATE_WIZARD_SECTION_START = 'components/create/section/section_start.html'
CREATE_WIZARD_SECTION_END = 'components/create/section/section_end.html'
CREATE_WIZARD_INPUT_DIR = 'components/create/inputs'

'''
    Used to strip userdata from models when JSONifying them
        e.g. user account, user profile, membership
'''
USERDATA_MODELS = [str(User)]
STRIPPED_FIELDS = ['SearchVectorField']

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
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "field_type": "string_inputbox",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": True
        },
        "is_base_field": True
    },
    "definition": {
        "title": "Definition",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "field_type": "textarea_markdown",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": False
        },
        "is_base_field": True
    },
    "implementation": {
        "title": "Implementation",
        "field_type": "textarea_markdown",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": False
        },
        "is_base_field": True
    },
    "publications": {
        "title": "Publications",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "field_type": "string_list_of_inputboxes",
        "active": True,
        "validation": {
            "type": "string_array",
            "mandatory": False
        },
        "is_base_field": True
    },
    "validation": {
        "title": "Validation",
        "field_type": "textarea_markdown",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": False
        },
        "is_base_field": True
    },
    "citation_requirements": {
        "title": "Citation Requirements",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "field_type": "textarea_markdown",
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
        "hide_on_create": True,
        "is_base_field": True
    },
    "author": {
        "title": "Author",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "field_type": "string_inputbox",
        "active": True,
        "validation": {
            "type": "string",
            "mandatory": True
        },
        "is_base_field": True
    },
    "collections": {
        "title": "Collections",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "field_type": "collections",
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
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "field_type": "tags",
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
    "group": {
        "title": "Group",
        "field_type": "group_field",
        "active": True,
        "validation": {
            "type": "int",
            "mandatory": True
        },
        "is_base_field": True
    },
    "updated": {
        "title": "Updated",
        "field_type": "???",
        "active": True,
        "validation": {
            "type": "datetime",
            "mandatory": True,
            "computed": True
        },
        "hide_on_create": True,
        "is_base_field": True
    },
    "created_by": {
        "title": "Created By",
        "field_type": "???",
        "active": True,
        "requires_auth": True,
        "validation": {
            "type": "int", 
            "mandatory": True,
            "computed": True
        },
        "hide_on_create": True,
        "is_base_field": True
    },
    "updated_by": {
        "title": "Updated By",
        "field_type": "???",
        "active": True,
        "requires_auth": True,
        "validation": {
            "type": "int", 
            "mandatory": True,
            "computed": True
        },
        "hide_on_create": True,
        "is_base_field": True
    },
}

'''
    Describes the input and output presentation of common and dynamic fields
    through components and modifiers
'''
FIELD_TYPES = {
    "int": {
        "data_type": "int",
        "input_type": "inputbox"
    },
    "date": {
        "data_type": "date",
        "input_type": "datepicker"
    },
    "daterange": {
        "data_type": "date",
        "input_type": "datepicker_range"
    },
    "string_inputbox": {
        "data_type": "string",
        "input_type": "inputbox",
        "max_length": 250
    },
    "string_inputbox_code": {
        "data_type": "string",
        "input_type": "inputbox",
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
        "input_type": "markdown",
        "rows": 5,
        "display": "markdown"
    },
    "string_list_of_inputboxes": {
        "data_type": "string",
        "input_type": "clinical/publication",
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

    "enum_radio_badge": {
        "data_type": "int",
        "input_type": "radiobutton",
        "use_permitted_values": True,
        "apply_badge_style": True
    },

    "enum_dropdown_badge": {
        "data_type": "int",
        "input_type": "dropdown",
        "use_permitted_values": True,
        "apply_badge_style": True
    },

    "concept_information": {
        "system_defined": True,
        "description": "json of concept ids/ver used in phenotype (managed by code snippet)",
        "input_type": "clinical/concept"
    },
    "coding_system": {
        "system_defined": True,
        "description": "list of coding system ids (calculated from phenotype concepts) (managed by code snippet)"
    },
    "tags": {
        "system_defined": True,
        "description": "list of tags ids (managed by code snippet)",
        "input_type": "tagbox"
    },
    "collections": {
        "system_defined": True,
        "description": "list of collections ids (managed by code snippet)",
        "input_type": "tagbox"
    },
    "data_sources": {
        "system_defined": True,
        "description": "list of data_sources ids (managed by code snippet)",
        "input_type": "tagbox"
    },
    "phenoflowid": {
        "system_defined": True,
        "description": "URL for phenoflow (managed by code snippet)"
    },

    "group_field": {
        "input_type": "group_select",
    },
}

#####################################

