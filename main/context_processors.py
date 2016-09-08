# coding: utf-8

from django.conf import settings


def preload(request):
    return {key: getattr(settings, key, '')
                for key in getattr(settings, 'EXPORT_KEYS', [])}
