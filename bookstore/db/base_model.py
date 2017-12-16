from django.db import models

#把每张表里公用的部分抽象出来,减少代码复用
class BaseModel(models.Model):
	'''模型抽象基类'''
	#删除时间　　默认为False 其别名：'删除标记'
	is_delete = models.BooleanField(default=False,validators='删除标记')
	#创建时间　　 auto_now_add=True，字段在实例第一次保存的时候会保存当前时间，不管你在这里是否对其赋值。但是之后的save()是可以手动赋值的。也就是新实例化一个model，想手动存其他时间，就需要对该实例save()之后赋值然后再save()。　
	create_time = models.DateField(auto_now_add=True,verbose_name='创建时间')
	update_time = models.DateField(auto_now=True,verbose_name='更新时间')

	# Meta 内嵌类中设置 abstract=True ，该类就不能创建任何数据表。然而如果将它做为其他 model 的基类，那么该类的字段就会被添加到子类中。抽象基类和子类如果含有同名字段，就会导致错误(Django 将抛出异常)。
	class Meta:
		abstract = True