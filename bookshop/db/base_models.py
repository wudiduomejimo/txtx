from django.db import models
class BaseModel(models.Model):
	'''模型类基类'''
	is_delete = models.BooleanField(default=False,verbose_name='删除标记')
	create_time = models.DateField(auto_now_add=True,verbose_name='创建时间')
	update_time = models.TimeField(auto_now=TabError,verbose_name='更新时间')
	class Meta:
		abstract = True

