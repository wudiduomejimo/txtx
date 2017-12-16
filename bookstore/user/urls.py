from django.conf.urls import url
from .views import register,login,logout,user,address,order,verifycode

urlpatterns = [
    url(r'^register/$',register,name='register'),
    url(r'^login/$',login,name='login'),
    url(r'^logout/$',logout,name='logout'),
    url(r'^user/',user,name='user'),
    url(r'^address/',address,name='address'),
    url(r'^order/',order,name='order'),
    url(r'^verifycode/$',verifycode, name='verifycode'), # 验证码功能
]
