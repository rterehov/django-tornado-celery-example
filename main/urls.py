from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from rest_framework import routers
from api.viewsets import TaskViewset
router = routers.DefaultRouter()
router.register(r'tasks', TaskViewset)

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list$', views.list_view, name='list'),
    url(r'^create$', views.index, name='create'),
    url(r'^cancel$', views.cancel, name='cancel'),
    url(r'^cancel/(?P<pk>\d+)$', views.cancel, name='cancel_task'),
    url(r'^delete$', views.delete, name='delete'),
    url(r'^delete/(?P<pk>\d+)$', views.delete, name='delete_task'),
    url(r'^', include(router.urls)),
]

urlpatterns += \
    static(settings.STATIC_URL, document_root=settings.STATIC_DIR)

urlpatterns += \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)