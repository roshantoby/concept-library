from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.views.generic.base import TemplateResponseMixin, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware

from clinicalcode.models.GenericEntity import GenericEntity
from clinicalcode.models.PublishedGenericEntity import PublishedGenericEntity
from ..entity_utils import publish_utils, permission_utils, constants
from datetime import datetime

class EntityDecline(LoginRequiredMixin, permission_utils.HasAccessToViewGenericEntityCheckMixin, TemplateResponseMixin, View):
    '''
        Decline the current working set.
    '''
    model = GenericEntity
    #use same template as we have two buttons publish and decline
    template_name = 'clinicalcode/generic_entity/publish/publish.html'

    @method_decorator([login_required, permission_utils.redirect_readonly])
    def post(self, request, pk, history_id):
        """
        Send request to server to decline entity
        @param request: user request object
        @param pk: entity id 
        @param history_id: entity historical id 
        @return: JSON response to the page
        """
        is_published = permission_utils.check_if_published(GenericEntity, pk, history_id)
        checks = publish_utils.check_entity_to_publish(request, pk, history_id)
        # if not is_published:
        #     checks = publish_utils.check_entity_to_publish(request, pk, history_id)

        data = dict()
        if not checks['allowed_to_publish'] or is_published:
            data['form_is_valid'] = False
            data['message'] = render_to_string('clinicalcode/error.html', {}, self.request)
            return JsonResponse(data)

        try:
            # start a transaction
            with transaction.atomic():
                entity = GenericEntity.objects.get(pk=pk)
                #if moderator and in pending state
                if checks['is_moderator'] and checks['approval_status'] == constants.APPROVAL_STATUS.PENDING:
                    published_entity = PublishedGenericEntity.objects.filter(entity_id=entity.id,entity_history_id=history_id,approval_status=constants.APPROVAL_STATUS.PENDING).first() #find first record
                    published_entity.approval_status = constants.APPROVAL_STATUS.REJECTED
                    
                    published_entity.save()
                    data['form_is_valid'] = True
                    data['approval_status'] = constants.APPROVAL_STATUS.REJECTED
                    data['entity_name_requested'] = GenericEntity.history.get(id=pk, history_id=history_id).name
                    data = publish_utils.form_validation(request, data, history_id, pk, entity, checks)
        except Exception as e:
            #print(e)
            data['form_is_valid'] = False
            data['message'] = render_to_string('clinicalcode/error.html', {}, self.request)

        return JsonResponse(data)
