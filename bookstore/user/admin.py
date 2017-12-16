
from django.contrib import admin
from user.models import Address,Passport
# Register your models here.
admin.site.register(Address)#在admin中添加有关商品编辑的功能
admin.site.register(Passport)#在admin中添加有关商品编辑的功能


