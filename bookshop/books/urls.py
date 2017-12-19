from django.conf.urls import url
from .views import index,detail

urlpatterns = [
    url(r'^index', index, name='index'),
    url(r'^books/(?P<books_id>\d+)/$', detail, name='detail'),
]
