# encoding: utf-8

from django.conf import settings

from rest_framework import viewsets, mixins

from ..models import Task
from ..api import serializers


class TaskViewset(viewsets.ReadOnlyModelViewSet, mixins.ListModelMixin):
    queryset = Task.objects.all().order_by('-pk')
    serializer_class = serializers.TaskSerializer

    def list(self, request):
        response = super(TaskViewset, self).list(request)
        response.data['page'] = request.query_params.get('page', 1)
        response.data['pages'] = \
            (response.data['count'] / settings.REST_FRAMEWORK['PAGE_SIZE'])
        if (response.data['count'] % settings.REST_FRAMEWORK['PAGE_SIZE']):
            response.data['pages'] += 1
        return response