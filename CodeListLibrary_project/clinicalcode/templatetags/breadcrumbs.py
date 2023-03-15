from django import template
from django.conf import settings
from jinja2.exceptions import TemplateSyntaxError
from django import urls
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import re
import difflib

register = template.Library()

def try_add_crumb(crumbs, crumb):
    if crumb in settings.BREADCRUMB_MAP:
        crumbs.append(settings.BREADCRUMB_MAP[crumb])

def generate_breadcrumbs(crumbs, header=False):
    output = ''
    if len(crumbs) <= 0:
        return output

    if header:
        output += '<header class="breadcrumb-header">'
    
    output += '<section class="breadcrumbs">'
    for i, crumb in enumerate(crumbs):
        url = crumb['url'] if i == len(crumbs) - 1 or i == 0 else reverse(crumb['url'])
        title = _(crumb['title'])
        output += '<span class="breadcrumb-item">' \
                        '<span class="marker"></span>' \
                        '<span class="breadcrumb">' \
                            f'<a href="{url}">{title}</a>' \
                        '</span>' \
                    '</span>'
    
    output += '</section>'

    if header:
        output += '</header>'

    return output

def find_matching_url(items, desired):
    for item in items:
        if isinstance(item, urls.URLResolver):
            match = find_matching_url(item.url_patterns, desired)
            if match:
                return match
        elif isinstance(item, urls.URLPattern):
            if item.name == desired or str(item.pattern).replace('/', '') == desired:
                return item
  
    return None

def get_url(desired):
    desired = 'concept_library_home' if desired == '' else desired
    url_resolver = urls.get_resolver(urls.get_urlconf())
    matching = find_matching_url(url_resolver.url_patterns, desired)
    if matching is not None:
        return matching, False
    
    resolver_items = {v[1].replace(re.sub('(\w+(?:$|\/))+', '', v[1]), ''):[k, v[1]] for k, v in urls.get_resolver(None).reverse_dict.items()}
    resolvers = [k for k in resolver_items]
    resolvers = difflib.get_close_matches(desired, resolvers, cutoff=0.3)
    
    if len(resolvers) > 0:
        resolvers = resolver_items.get(resolvers[0])
        token = re.sub('(\w+(?:$|\/))+', '', resolvers[1])
        matched_url = find_matching_url(url_resolver.url_patterns, resolvers[0])
        
        return matched_url, len(token) > 1

    return None, False

@register.tag
def breadcrumbs(parser, token):
    params = {
        'useMap': False,
        'useName': True,
        'includeHome': False,
        'includeHeader': False,
    }

    try:
        parsed = token.split_contents()[1:]
        for param in parsed:
            ctx = param.split('=')
            params[ctx[0]] = eval(ctx[1])

    except ValueError:
        raise TemplateSyntaxError("Unable to parse breadcrumbs")

    nodelist = parser.parse(('endbreadcrumbs',))
    parser.delete_first_token()
    return BreadcrumbsNode(params, nodelist)


class BreadcrumbsNode(template.Node):
    DEFAULT_STR = '<section class="breadcrumbs"></section>'
    
    def __init__(self, params, nodelist):
        self.request = template.Variable('request')
        self.params = params
        self.nodelist = nodelist

    def get_crumb(self, crumb, url):
        if self.params['useName']:
            return re.sub('(\-|\_)+', ' ', url.name).title()

        return crumb.title()

    def map_path(self, path, rqst):
        crumbs = []
        for i, crumb in enumerate(path):
            if crumb == '':
                if self.params['includeHome']:
                    try_add_crumb(crumbs, 'concept_library_home')
            else:
                try_add_crumb(crumbs, crumb)
      
        if len(crumbs) > 0:
            crumbs[-1]['url'] = rqst.get_full_path()

        if len(crumbs) > 1:
            return generate_breadcrumbs(crumbs, header=self.params['includeHeader'])
        else:
            return ''

    def map_resolver(self, path, rqst):
        crumbs = []
        if self.params['includeHome']:
            crumbs.append({ 'url': '/', 'title': 'Home' })
        
        token_next = False
        for i, crumb in enumerate(path):
            if token_next:
                break
            
            if crumb != '':
                url, token_next = get_url(crumb)
                if url:
                    root = ''
                    look_up = url.lookup_str.split('.')
                    if look_up[0] == 'apps':
                        root = f'{look_up[1]}:'
                
                    crumbs.append({ 'url': root + url.name, 'title': 'Home' if crumb == '' else self.get_crumb(crumb, url) })

        if len(crumbs) > 0 and crumbs[-1]['title'] != 'Home':
            crumbs[-1]['url'] = rqst.get_full_path()
        
        if len(crumbs) > 1:
            return generate_breadcrumbs(crumbs, header=self.params['includeHeader'])
        else:
            return ''

    def render(self, context):
        rqst = self.request.resolve(context)
        path = rqst.get_full_path().split('/')

        if len(path) > 0:
            if self.params['useMap']:
                return self.map_path(path, rqst)
            else:
                return self.map_resolver(path, rqst)
        
        output = self.DEFAULT_STR

        return output