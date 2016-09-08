# coding: utf-8

import json
import urllib
import traceback
import random
import brukva
import datetime
import urlparse

from tornado import httpclient
from tornado import ioloop

from sockjs.tornado import SockJSConnection

from django.conf import settings

from django_redis import get_redis_connection

from models import Task


def get_brukva():
    print 'Get Brukva connect with: %s:%s:%s' % \
        (settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)
    try:
        c = brukva.Client(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                          selected_db=settings.REDIS_DB)
        c.connect()
    except:
        print traceback.format_exc()
    else:
        print 'Ok'
    return c


c = get_brukva()
r = get_redis_connection('redis')


class TornadoSockJS(SockJSConnection):
    """
    Торнадо-сервер для обслуживания зарпросов о состоянии фоновых задач.

    """
    def __init__(self, *args, **kwargs):
        super(TornadoSockJS, self).__init__(*args, **kwargs)
        self.client = get_brukva()
        self.client_id = random.randint(10000, 99999)
        self.task_id = ''

        # Показывает, находится ли процесс в процессе получения данных.
        # Нужен, чтобы не плодить коннекты к API.
        self.work = False

        # Показывает, что клиент отключился
        self.closed = False

    def on_open(self, request):
        self.__log('[on_open] ok')

    def on_close(self):
        """
        Закрытие соединения с клиентом.

        """
        def after_unsubscribe(a):
            self.client.disconnect()

        self.closed = True
        self.__log('[on_close] start')
        if self.client.subscribed:
            self.client.unsubscribe(self.channel, after_unsubscribe)
            self.__log('client unsubscribe ok')
        self.client.disconnect()
        self.__log('[on_close] ok')

    def on_message(self, message):
        """
        Пришло сообщение от клиента.

        Список возможных сообщений:
        connect     Подключить клиента к конкретному таску.
        
        """
        data = json.loads(message)
        if data['type'] == 'connect':
            self.connect_to_task(data['task_id'])
        else:
            self.__log('Undefined message, skip...')

    ### Блок функций для работы с задачами
    def connect_to_task(self, task_id):
        """
        Подключаем клиента к конкретной задаче и начинаем опрос состояния
        задачи.

        """
        self.task_id = task_id
        if not self.task_id:
            self.__log('ERROR, bad task ID')
            self.close()
            return

        self.__log('[connect_to_task] start: %s' % (task_id,))
        if not Task.objects.filter(pk=self.task_id).exists():
            self.__log('ERROR, task does not exist')
            self.close()
            return

        # подписываемся на канал
        self.channel = 'tornado:task:{}'.format(self.task_id)
        self.client.subscribe(self.channel)
        self.__log('[connect_to_task] ok')
        
        # Cпрашиваем статус задачи
        if not self.work:
            self.get_status() 

    def get_status(self):
        """       
        Получает статус задачи.

        url вшиваем для быстродействия, т.к. нет уверенности, что reverse будет
        выполняться неблокирующим образом

        """
        # Если клиент был отключен, то нет смысла делать запросы на API.
        if self.closed:
            return

        self.work = True
        try:
            self.__make_http_request(settings.API_GET_STATUS_URL % (self.task_id))
        except:
            self.work = False

    def process_status(self, status):
        '''
        Рассылаем статус клиентам и планируем новое получение статуса.

        '''
        # рассылаем клиентам
        super(TornadoSockJS, self).send(status)

        # планируем следующий опрос задачи
        ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(seconds=settings.TORNADO_TIMEOUT),
            self.get_status)


    ### Блок функций для работы с внешним API
    def __make_http_request(self, url, method='GET', body=None):
        """
        Служит для создания асинхронных запросов на внешний API. Так сделано
        для того, чтобы не блокировать цикл торнадо. Мы посылаем запрос
        и обрабатываем ответ только когда он приходит.

        """
        self.__log('[make_http_request] {}'.format(url))
        request = httpclient.HTTPRequest(
                    url,
                    method=method,
                    validate_cert=settings.TORNADO_VALIDATE_CERT)
        httpclient.AsyncHTTPClient().fetch(request, self.__handle_request)

    def __handle_request(self, response):
        """
        Обработка ответа на ранее сделанный http запрос.

        """
        if response.error:
            self.__log('[error] %s' % (response.error))

        data = json.loads(response.body)
        if data.get('image', None):
            scheme, netloc, path, params, query_string, fragment = urlparse.urlparse(data['image'])
            data['image'] = urlparse.urlunsplit(('', '', path, query_string, fragment))
        self.process_status(json.dumps(data))

    def __log(self, msg):
        if settings.TORNADO_DEBUG:
            print "[%s] %s: %s" % (self.client_id, self.task_id, msg)
