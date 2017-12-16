from django.conf.urls import url
from .views import comment

urlpatterns = [
    url(r'^comment',comment,name='comment'),

]
