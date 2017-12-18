from django.db import models
from db.base_models import BaseModel
from hashlib import sha1
# Create your models here.

def get_hash(str):
	'''取一个字符串的hash值'''
	sh = sha1()
	sh.update(str.encode('utf8'))
	return sh.hexdigest()

class PassportManager(models.Manager):
	def add_one_passport(self,username,password,email):
		'''添加一个帐户信息'''
		passport = self.create(username=username,password=get_hash(password),email=email)
		return passport
	def get_one_passport(self,username,password):
		'''根据用户名密码查找帐户'''
		try:
			passport = self.get(username=username,password=get_hash(password))
		#异常的基类会为所有模型捕获到所有DoesNotExist 异常
		except self.model.DoesNotExist:
			#帐户不存在
			passport = None
		return passport
	def get_passport(self,username):
		'''判断用户名是否被注册'''
		try:
			passport = self.get(username=username)
		except self.model.DoesNotExist:
			#帐户不存在
			passport = None
		return passport


class Passport(BaseModel):
	username = models.CharField(max_length=20,verbose_name='用户名')
	password = models.CharField(max_length=200,verbose_name='密码')#防止加密后数据太长
	email = models.EmailField(verbose_name='邮箱')
	is_active = models.BooleanField(default=False,verbose_name='激活状态')

	objects = PassportManager()
	class Meta:
		db_table = 's_user_account'



