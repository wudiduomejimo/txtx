from django.db import models
from db.base_model import BaseModel
from user.models import Passport
from books.models import Books
# Create your models here.

class OrderInfoManger(models.Manager):
	'''订单信息模型管理器'''
	pass

#订单详情表　外键用户表和地址表
class OrderInfo(BaseModel):
	PAY_METHOD_CHOICES = (
		(1,'货到付款'),
		(2,'微信支付'),
		(3,'支付宝'),
		(4,'银联支付'),
	)

	PAY_METHOD_ENUM = {
		'CASH':1,
		'WEIXIN':2,
		'ALIPAY':3,
		'UNIONPAY':4,
	}

	ORDER_STATUS_CHOICES = (
		(1,'待支付'),
		(2,'待发货'),
		(3,'待收货'),
		(4,'待评价'),
		(5,'已完成'),
	)
	order_id = models.CharField(max_length=64,primary_key=True,verbose_name='订单编号')
	passport = models.ForeignKey('user.Passport',verbose_name='下单账户')
	addr = models.ForeignKey('user.Address',verbose_name='收货地址')
	total_count = models.IntegerField(default=1,verbose_name='商品总数')
	total_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品总价')
	transit_price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='订单运费')
	pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES,default=1,verbose_name='支付方式')
	status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,default=1,verbose_name='订单状态')
	trade_id = models.CharField(max_length=100,unique=True,null=True,blank=True,verbose_name='支付编号')

	objects = OrderInfoManger()

	class Meta:
		db_table = 's_order_info'


	# 由于每一笔订单都是由不同的商品组成，所以我们需要把一笔订单拆分开，来建立一个订单中每种商品的信息数据表。关系数据库的一个好处就是强约束，冗余也很少，这点比mongodb好。
class OrderGoodsManager(models.Manager):
	'''订单商品墨香管理器类'''
	pass


class OrderGoods(BaseModel):
	order = models.ForeignKey('OrderInfo',verbose_name='所属订单')
	books = models.ForeignKey('books.Books',verbose_name='订单商品')
	count = models.IntegerField(default=1,verbose_name='商品数量')
	price = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品价格')

	objects = OrderGoodsManager()

	class Meta:
		db_table = 's_order_books'
