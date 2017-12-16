from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from utils.decorators import login_required
from django.http import HttpResponse,JsonResponse
from user.models import Address
from books.models import Books
from order.models import OrderInfo,OrderGoods
from django_redis import get_redis_connection
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import os
import time
from django.db import transaction
# Create your views here.

#购物车页面点击去结算得到商品id　把数据传到订单页面显示
def order_place(request):
	'''显示提交订单页面'''
	#接收数据 获取要提交的所有书的id
	books_ids = request.POST.getlist('books_ids')
	#校验数据
	if not books_ids:
		# 跳转购物车页面
		return redirect(reverse('cart:show'))
	if not all(books_ids):
		#跳转购物车页面
		return redirect(reverse('cart:show'))

	#用户收货地址　得到用户id　根据用户id获取地址
	passport_id = request.session.get('passport_id')
	addr = Address.objects.get_default_address(passport_id=passport_id)
	#用户要购买商品的信息
	books_li = []
	total_count = 0
	total_price = 0

	conn = get_redis_connection('default')
	cart_key = 'cart_%d'%passport_id

	for id in books_ids:
		#根据id获取商品信息
		books = Books.objects.get_books_by_id(books_id=id)
		#从redis中获取商品数量
		count = conn.hget(cart_key,id)
		#把商品的数量保存在book的属性中
		books.count = count
		#计算商品小计
		amout = int(count)*books.price
		# 把商品的总价保存在book的属性中
		books.amout = amout
		books_li.append(books)

		#累计计算商品的数目和总金额
		total_count += int(count)
		total_price += books.amout

	#商品运费和实付款
	transit_price = 10
	total_pay = total_price + transit_price

	#1 2 3
	books_ids = ','.join(books_ids)
	#组织模板上下文
	context = {

		'addr':addr,
		'books_li':books_li,
		'total_count':total_count,
		'total_price':total_price,
		'transit_price':transit_price,
		'total_pay':total_pay,
		'books_ids':books_ids,
	}

	#使用模板
	return render(request,'order/place_order.html',context)




#点击提交订单
@csrf_exempt # 不加ajax不能传输　前端报403
@transaction.atomic #事物
def order_commit(request):
	'''生成订单'''
	#验证用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'用户登录'})

	#接受数据
	addr_id = request.POST.get('addr_id')
	pay_method = request.POST.get('pay_method')
	books_ids = request.POST.get('books_ids')
	#进行数据校验
	if not all([addr_id,pay_method,books_ids]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})
	try:
		addr = Address.objects.get(id=addr_id)
	except Exception as e:
		#地址信息出错
		return JsonResponse({'res':2,'errmsg':'地址信息出错'})
	if int(pay_method) not in OrderInfo.PAY_METHOD_ENUM.values():#装有支付方式的常量的字典
		return JsonResponse({'res':1,'errmsg':'不支持的支付方式'})

	#订单创建
	#组织订单信息　用户id
	passport_id = request.session.get('passport_id')
	#订单id　时间戳　＋　用户id　确保订单id的唯一性
	order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(passport_id)
	print(order_id)
	#运费
	transit_price = 10
	#订单商品总数和总金额
	total_count = 0
	total_price = 0
	try:
		#创建一个保存点
		sid = transaction.savepoint()
		#向订单信息表中添加一条记录
		order = OrderInfo.objects.create(
			order_id=order_id,
			passport_id=passport_id,
			addr_id=addr_id,
			total_count=total_count,
			total_price=total_price,
			transit_price=transit_price,
			pay_method=pay_method
		)

		#向订单商品表中添加订单商品记录
		#books_ids　传过来的类型是'1,3,6,4'　通过','把它转换成[1,3,6,4] 　
		books_ids = books_ids.split(',')
		conn = get_redis_connection('default')
		cart_key = 'cart_%d'%passport_id

		#遍历获取用户购买的商品信息
		for id in books_ids:
			books = Books.objects.get_books_by_id(books_id=id)
			if books is None:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res':4,'errmsg':'商品信息错误'})

			count = conn.hget(cart_key,id)
			#判断商品库存
			if int(count) > books.stock:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res':5,'errmsg':'商品库存不足'})

			#创建一条订单商品记录
			OrderGoods.objects.create(order_id=order_id,
									  books_id=id,
									  count = count,
									  price=books.price
														)
			#增加商品的销量,减少商品库存
			books.sales += int(count)
			books.stock -= int(count)
			books.save()

			#累计计算商品的总数目和总金额
			total_count += int(count)
			total_price += int(count)*books.price
		#更新订单的商品总数目和总金额
		order.total_count = total_count
		order.total_price = total_price
		order.save()
	except	Exception as e:
		print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'res':7,'errmsg':'服务器错误'})

	#清除购物车对应的记录
	conn.hdel(cart_key,*books_ids)
	#事务提交
	transaction.savepoint_commit(sid)
	#返回应答
	return JsonResponse({'res':6})







def order(request):
	'''用户中心订单页'''
	#查询用户的订单信息
	passport_id = request.session.get('passport_id')
	#获取订单信息
	order_li = OrderInfo.objects.filter(passport_id=passport_id)
	#遍历获取订单的商品信息
	#order > OrderInfo　实例对象
	for order in order_li:
		order_id = order.order_id
		order_books_li = OrderGoods.objects.filter(order_id=order_id)
		#计算商品小计
		#order_books > OrderBooks实例对象
	for order_books in order_books_li:
		count = order_books.count
		price = order_books.price
		amount = count*price
		#保存订单中每一个商品的小计
		order_books.amount = amount
		#给order对象动态添加一个属性order_goods_li保存订单中商品的信息
		context = {
			'order_li':order_li,
			'page':'order'

		}

	return render(request,'user/user_center_order.html/')


'''

#前端发过来的参数order_id
def order_pay(request):
	#用户登录判断
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'用户未登录'})
	#接受订单id
	order_id = request.POST.GET('order_id')
	#数据校验
	if not order_id:
		return JsonResponse({'res':1,'errmsg':'订单不存在'})
	try:
		order = OrderInfo.objects.get(order_id=order_id,status=1,pay_method=3)
	except OrderInfo.DoesNotExist:
		return JsonResponse({'res':2,'errmsg':'订单信息出错'})

	#和支付宝进行交互
	alipay = AliPay(
		appid='2016090800464054',
		app_notify_url = None
		app_private_key_path = os.path.join(settings.)





	)



'''







