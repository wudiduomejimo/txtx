from django.conf.urls import url
from .views import order_place,order_commit

urlpatterns = [
    url(r'^place',order_place,name='place'),
    url(r'^commit',order_commit,name='commit'),
]
