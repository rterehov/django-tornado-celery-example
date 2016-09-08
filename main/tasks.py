# coding:utf-8

import os
import time
import requests
import opengraph
import hashlib
import urlparse

from scrapy import Selector
from urlparse import parse_qs, urlsplit, urlunsplit
from random import randint

from django.conf import settings
from django.utils import timezone
from django.core.files import File

from celery import task, current_task
from celery.result import AsyncResult

from .models import Task

# Снижаем вероятность обнаружения подозрительной активности
user_agents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.5.17 (KHTML, like Gecko) Version/9.1 Safari/601.5.17',
    'Mozilla/5.0 (iPad; CPU OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13D15 Safari/601.1',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0',
    # ...
]

    
@task()
def process(task_id):
    """
    Фоновый процесс.

    Парсит информацию по url, записывает ее в БД, после чего приступает к
    скачиванию картинки (если она есть).
    Картинка качается чанками по 0.01 от полного размера (для простого
    формирования прогресс-бара).
    На каждом этапе работы процесс меняет собственный статус.

    По коду расставлены паузы для того, чтобы на клиенте было удобней
    наблюдать за процессом.

    """
    process.update_state(state='BEGIN')
    task = Task.objects.get(pk=task_id)
    url = task.url

    process.update_state(state='GET TITLE')
    time.sleep(1)
    ua = user_agents[randint(0, len(user_agents)-1)]
    try:
        html = requests.get(url, verify=False, headers={'User-Agent': ua},
                            timeout=10).text
    except:
        process.update_state(state='Failure')
        task.completed = True
        task.save()
        return

    og = opengraph.OpenGraph(html=html)
    selector = Selector(text=html)
    task.title = og.get('title', '')
    task.save()

    process.update_state(state='GET H1')
    time.sleep(1)
    try:
        task.h1 = og.get('description', '')
        if not task.h1:
            task.h1 = selector.xpath('//h1/text()').extract()[0]
    except:
        task.h1 = ''
    task.save()

    process.update_state(state='GET IMG')
    time.sleep(1)
    try:
        img_url = og.get('image', '')
        if not img_url:
            img_url = selector.xpath('//img/@src').re('(.*?\.(?:png|jpg))')[0]
        scheme, netloc, path, params, query_string, fragment = urlparse.urlparse(img_url)
        if not scheme:
            if netloc:
                scheme, _, _, _, _ = urlsplit(url)
            else:
                scheme, netloc, _, _, _ = urlsplit(url)
            img_url = urlunsplit((scheme, netloc, path, query_string, fragment))
        task.img = img_url
    except:
        task.img = ''
    task.save()
    
    if task.img:
        def download(url, filename=None, force=None):
            """
            Download URI to local path

            """
            dir1 = os.path.join(settings.MEDIA_ROOT, 'downloads')
            if not os.path.exists(dir1):
                os.mkdir(dir1)
            path = '{}/{}'.format(dir1, filename)
            tmp_path = '{}/{}.bak'.format(dir1, filename)
            if os.path.exists(path) and not force:
                return path

            info = requests.head(url, timeout=5)
            counter = 0
            while info.is_permanent_redirect or info.is_redirect:
                counter += 1
                if counter > 3:
                    print 'Many redirects! Exit!'
                    return
                url = info.headers['Location']
                info = requests.head(url, timeout=5)

            if int(info.status_code) != 200:
                print 'Bad URL (head), status: '.format(url, info.status_code)
                return
            size = int(info.headers['Content-Length'])

            rr = requests.get(url, stream=True, timeout=5)
            if int(rr.status_code) != 200:
                print 'Bad URL, status: '.format(url, rr.status_code)
                return

            f = open(tmp_path, 'wb')
            progress = 0
            chunk_size = size / 100
            for i, chunk in enumerate(rr.iter_content(chunk_size=chunk_size)):
                if chunk:
                    f.write(chunk)
                    progress += 1
                    progress = 100 if progress > 100 else progress
                    process.update_state(state='DOWNLOAD IMG', meta={'progress': progress})
                    time.sleep(0.05)
                    
            process.update_state(state='DOWNLOAD IMG', meta={'progress': 100})
            f.close()
            os.rename(tmp_path, path)
            return path


        process.update_state(state='DOWNLOAD IMG', meta={'progress': 0})
        time.sleep(1)
        ex = task.img.split('.')[-1]
        filename = hashlib.md5(url).hexdigest() + ".{}".format(ex)
        path = download(task.img, filename=filename, force=True)
        if path:
            f = File(open(path, 'r'))
            task.image = f
            task.save()
            f.close()

    task.celery_id = None
    process.update_state(state='Complete!')
    task.completed = True
    task.save()


def get_task_status(task_id):
    """
    Получения статуса фоновой задачи по ее ID

    """
    task = process.AsyncResult(task_id) 
    progress = 0
    try:
        progress = task.info.get('progress', 0)
    except:
        pass
    return {
        'status': task.status,
        'progress': progress,
    }
