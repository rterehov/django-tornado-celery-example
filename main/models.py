# coding: utf-8

import os
import uuid
import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse


def get_uuid_image(instance, filename):
    """
    Генерация уникального имени файла для картинок

    """
    def uuid_name_generator(filename, prefix='', ext=None):
        if ext is None:
            ext = os.path.splitext(filename)[1]
        name = uuid.uuid4().hex + ext.lower()
        path = u'/'.join(filter(None, (prefix, name[:2], name[2:4], name)))
        return path
    prefix = "images"
    return uuid_name_generator(filename, prefix=prefix)


class Task(models.Model):
    """
    Задачи.

    """

    # url однозначно идентифицирует задачу
    url = models.CharField(u'Ссылка', max_length=256, blank=False, null=False, unique=True)

    # В этих полях храним данные, собранные парсером.
    title = models.CharField(u'Содержимое title', max_length=256, blank=True, null=False, default='')
    h1 = models.CharField(u'Содержимое h1', max_length=256, blank=True, null=False, default='')
    img = models.CharField(u'Ссылка на картинку', max_length=256, blank=True, null=False, default='')

    # Скачанная картинка.
    image = models.ImageField(u'Сохраненная картинка', null=True, blank=True, upload_to=get_uuid_image)

    start_at = models.DateTimeField(u'Время запуска', null=True, blank=False,
                                        default=timezone.now)

    # ID задачи в селери.
    celery_id = models.CharField(u'ID celery-задачи', null=True, blank=True, max_length=256)

    # Если флаг стоит, значит фоновая задача запускалась и завершилась. Ничего
    # не говорит о причине завершения.
    completed = models.BooleanField(default=False, null=False)

    @property
    def finished(self):
        """
        Если стоит флаг completed и нет идентификатора задания celery, то
        это означает, что задание отработало до конца и успешно завершилось

        """
        return self.completed and not self.celery_id

    @property
    def cancel_url(self):
        return reverse('cancel_task', args=(self.pk,))

    @property
    def status(self):
        """
        Статус задачи.

        """
        status = {
            'status': 'Pending...',
        }
        if self.celery_id:
            from .tasks import get_task_status
            status = get_task_status(self.celery_id)
        else:
            if self.completed:
                status = {'status': 'Completed!'}
            elif self.start_at < timezone.now():
                status = {
                    'status': 'Broken!'
                }
        return status
