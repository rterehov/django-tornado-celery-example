# encoding: utf-8
from rest_framework import serializers

from ..models import Task

        
class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'url', 'title', 'h1', 'img', 'image', 'start_at',
                    'celery_id', 'completed', 'status', 'cancel_url',
                    'finished')

