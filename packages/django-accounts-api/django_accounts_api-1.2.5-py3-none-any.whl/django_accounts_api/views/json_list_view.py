from django.core import serializers
from django.http import HttpResponse
from django.views.generic.list import BaseListView

class JsonListView(BaseListView):
    ''' Extends the django base list view to return json serialized data
    '''
    def render_to_response(self, context, **response_kwargs):
        queryset = self.get_queryset()
        response = HttpResponse(
           serializers.serialize("json", queryset, fields=self.get_fields())
        )
        response.headers['Content-Type'] = 'application/json'
        return response
