# coding: utf-8

from django.conf import settings
from django.http import Http404
from django.http import JsonResponse, HttpResponse
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView, View
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from extra_cbv.views.ajax import JsonView, UpdateAjaxFormMixin
from celery.task.control import revoke

from .forms import CreateForm
from .models import Task
from .utils import cancel_tasks


class IndexView(UpdateAjaxFormMixin, FormView):
    """
    Главная страница. Она же - форма для создания заданий.

    """
    form_class = CreateForm
    template_name = 'index.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        kwargs.update({
            'page': self.request.GET.get('page', 1),
        })
        if not kwargs.get('form'):
            kwargs['form'] = self.form_class()        
        return kwargs

index = IndexView.as_view()


class ListView(TemplateView):
    '''
    Список тасков с пейджинацией. Для аякс-запросов.

    '''
    template_name = 'list.html'

    def get_context_data(self, *args, **kwargs):
        page = int(self.request.GET.get('page', 1))
        tasks = Task.objects.all().order_by('-pk')
        paginator = Paginator(tasks, settings.PAGE_SIZE)
        try:
            tasks = paginator.page(page)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            if int(page) < 1:
                tasks = paginator.page(1)
            else:
                tasks = paginator.page(paginator.num_pages)
        kwargs.update({
            'tasks': tasks,            
        })
        return kwargs

list_view = ListView.as_view()


class CancelView(View):
    """
    Отмена выполнения всех заданий или одного конкретного.

    """
    http_method_names = [u'post']

    def __proc(*args, **kwargs):
        pk = kwargs.get('pk', None)
        qs = Task.objects.all()
        if pk:
            qs = qs.filter(pk=pk)
        cancel_tasks(qs)
        return JsonResponse({'status': 'ok'})

    def post(self, *args, **kwargs):
        return self.__proc(*args, **kwargs)

cancel = CancelView.as_view()


class DeleteView(View):
    """
    Удаление всех заданий. По ТЗ не требовалось. Сделано для удобства
    тестирования.

    """
    http_method_names = [u'post']

    def __proc(*args, **kwargs):
        pk = kwargs.get('pk', None)
        qs = Task.objects.all()
        if pk:
            qs = qs.filter(pk=pk)
        cancel_tasks(qs)
        qs.delete()
        return JsonResponse({'status': 'ok'})

    def post(self, *args, **kwargs):
        return self.__proc(*args, **kwargs)

delete = DeleteView.as_view()
