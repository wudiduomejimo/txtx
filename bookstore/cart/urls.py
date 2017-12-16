from django.conf.urls import url
from .views import car_add,cart_count,cart_show,cart_del,cart_update

urlpatterns = [

    url(r'^add',car_add,name='add'),
    url(r'^count',cart_count,name='count'),
    url(r'^show',cart_show,name='show'),
    url(r'^del',cart_del,name='del'),
    url(r'^update',cart_update,name='update'),

]
