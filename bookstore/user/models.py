from django.db import models
from hashlib import sha1
from db import base_model
# Create your models here.

#hash用来加密
def get_hash(str):
	'''取一个字符串的hash值'''
	sh = sha1()
	sh.update(str.encode('utf8'))
	return sh.hexdigest()

#自定义的管理器
class PassportManger(models.Manager):
	def add_one_passport(self, username, password, email):
		'''添加一个帐户信息'''
		passport = self.create(username=username, password=get_hash(password), email=email)
		return passport

	def get_one_passport(self, username, password):
		'''根据用户名密码查找帐户信息'''
		try:
			passport = self.get(username=username, password=get_hash(password))#get_hash函数用来给密码加密
		except self.model.DoesNotExist:
			# 帐户不存在
			passport = None
		return passport

#继承基类里的字段
class Passport(base_model.BaseModel):
	'''用户模型类'''
	username = models.CharField(max_length=20, verbose_name='用户名称')
	password = models.CharField(max_length=40, verbose_name='用户密码')
	email = models.EmailField(verbose_name='用户邮箱')
	is_active = models.BooleanField(default=False, verbose_name='激活状态')

	# 用户表的管理器,objects
	objects = PassportManger()

	#给表其别名
	class Meta:
		db_table = 's_user_account'

#自定义管理类
class AddressManager(models.Manager):
	'''地址类模型管理器'''
	def get_default_address(self,passport_id):
		'''指定用户的默认收货地址'''
		try:
			addr = self.get(passport_id=passport_id, is_default=True)
		except self.model.DoesNotExist:
			#没有默认收货地址
			addr = None
		return addr

	def add_one_address(self, passport_id, recipient_name, recipient_addr, zip_code, recipient_phone):
		'''添加收货地址'''
		#判断用户是否有默认收货地址
		addr = self.get_default_address(passport_id=passport_id)
		if addr:
			#存在默认地址
			is_default = False
		else:
			is_default = True
		#添加一个默认地址
		addr = self.create(passport_id=passport_id,
						   recipient_name=recipient_name,
						   recipient_addr=recipient_addr,
						   zip_code=zip_code,
						   recipient_phone=recipient_phone,
						   is_default=is_default)
		return addr

#地址
class Address(base_model.BaseModel):
	'''地址类模型'''
	recipient_name = models.CharField(max_length=20,verbose_name='收件人')
	recipient_addr = models.CharField(max_length=256,verbose_name='收件地址')
	zip_code = models.CharField(max_length=6,verbose_name='邮政编码')
	recipient_phone = models.CharField(max_length=11,verbose_name='手机号码')
	is_default =  models.BooleanField(default=False,verbose_name='是否默认')
	passport = models.ForeignKey('Passport',verbose_name='帐户')
	#外键和用户标关联
	objects = AddressManager()

	class Meta:
		db_table = 's_user_addres'

