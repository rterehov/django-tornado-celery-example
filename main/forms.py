# coding: utf-8

import string
import urlparse
import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import get_current_timezone

import validators

from .tasks import process
from .models import Task


class CreateForm(forms.Form):
    """
    Форма для создания новых задач.

    """
    urls = forms.CharField(required=True, label=u"URLS",
        widget=forms.Textarea(attrs={'rows': '5', 'cols': '66'}))
    time = forms.CharField(required=False, label=u"Время",
        widget=forms.DateTimeInput(attrs={'size': 30}))

    def clean_urls(self):
        urls = self.cleaned_data['urls']
        urls = set(map(lambda x: x.strip(), urls.split('\n')))
        if len(urls) > 5:
            raise ValidationError(u'Разрешено не более 5 URL.')

        if Task.objects.filter(
            completed=False, celery_id__isnull=False
        ).count() >= 5:
            raise ValidationError(u'Подождите, есть 5 задач, которые еще не подверглись парсингу.')

        bad = [url for url in urls if not validators.url(url)]
        if bad:
            raise ValidationError(u'Неправильные урлы ({})'.format(bad))

        return urls

    def clean_time(self):
        res = None
        time = self.cleaned_data['time']
        if time:
            try:
                res = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                if settings.USE_TZ:
                    tz = get_current_timezone()
                    res = tz.localize(res)
            except:
                raise ValidationError(u'Неверный формат времени')
        return res

    def save(self):
        """
        Создание задач.
        Если задача уже есть, то процесс инициируется повторно.

        """
        urls = self.cleaned_data['urls']
        time = self.cleaned_data['time']
        for url in urls:
            task, create = Task.objects.update_or_create(url=url)
            if task:
                now = timezone.now()
                if time:
                    task.start_at = time if time > now else now
                else:
                    task.start_at = now
                task.title = ''
                task.h1 = ''
                task.img = ''
                task.image = None
                task.completed = False
                task.save()

                # Стартуем задачу через 3с, чтобы наблюдать некоторое время
                # статус PENDING в интерфейсе.
                proc = process.apply_async((task.pk,), \
                            countdown=(task.start_at - now).seconds or 3)

                task.celery_id = proc.id
                task.save()
