from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from django_redis import get_redis_connection
from utils.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@login_required
def cart_show(request):#点击详情页面的我的购物车跳转
	'''显示用户购物车记录'''
	#获取用户的id
	passport_id = request.session.get('passport_id')
	#获取用户购物车的记录
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id
	#取出购物车里所有的纪录
	res_dict = conn.hgetall(cart_key)
	books_li = []
	#保存所有商品的总数
	total_count = 0
	#保存所有商品的总价格
	total_price = 0

	#遍历res_dict获取商品的数据
	for id,count in res_dict.items():
		#根据id获取商品信息
		books = Books.objects.get_books_by_id(books_id=id)
		#保存商品的数目
		books.count = count
		#保存商品的小计
		books.amount = int(count) * books.price
		books_li.append(books)

		total_count += int(count)
		total_price += int(count) * books.price

	#定义上下文模板
	context = {
		'books_li': books_li,
		'total_count':total_count,
		'total_price':total_price,

	}
	return render(request,'cart/cart.html',context)


#点击详情页面的加入购物车
def car_add(request):
	'''向购物车添加数据'''
	#1.判断是否登陆　2．对数据进行校验　3.判断商品是否存在　4.判断商品是否存在　5.判断库存　6.加入redis
	#判断用户是否登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登陆'})

	#接受数据　前端设置加入购物车单击响应函数，并获取books_id,books_count，用ajax传到后端
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')
	#进行数据校验
	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		#商品不存在
		return JsonResponse({'res':2,'errmag':'商品不存在'})
	try:
		count = int(books_count)
	except Exception as e:
		return JsonResponse({'res':3,'errmsg':'商品数量必须为数字'})
	#添加商品到购物车，点击添加到购物车把数据保存到redis中
	#每个用户的购物车记录用一天hash数据保存，格式:cart_用户id:商品id商品数量
	conn = get_redis_connection('default')
	#根据用户id号设置购物车id
	cart_key = 'cart_%d'%request.session.get('passport_id')
	#得到购物车里商品的数量
	res = conn.hget(cart_key,books_id)
	if res is None:
		#如果用户的购物车中没有添加过该商品，则添加数据
		res = count
	else:
		#如果用户的购物车添加了该商品，则累计商品数目（在redis中）
		res = int(res) + count
	#判断商品的库存
	if res > books.stock:
		return JsonResponse({'res':4,'errmsg':'商品库存不足'})
	else:
		#写入redis
		conn.hset(cart_key,books_id,res)
	#返回结果
	return JsonResponse({'res':5})



#购物车中商品的总共数量（购物车页面发送get请求调用）进入购物车时商品的数量
def cart_count(request):
	'''获取用户购物车中的商品数目'''
	#1.判断是否在线 2.根据购物车id获取所有的商品数量 3.遍历商品列表计算商品数量
	#判断用户是否在线
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0})

	#计算用户购物车商品数目
	conn = get_redis_connection('default')
	cart_key = 'cart_%d'%request.session.get('passport_id')
	res = 0
	#根据购物车id获取所有的商品数量
	res_list = conn.hvals(cart_key)

	for i in res_list:
		res += int(i)
	#返回结果
	return JsonResponse({'res':res})




#前端穿过来的参数　商品id books_id
#post
#/cart/del/
@csrf_exempt
def cart_del(request):
	'''删除用户购物车中的商品信息'''
	#1.得到前端穿过来要删除的商品id 2.校验数据　3.从redis删除
	#判断用户是否登陆

	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登陆'})
	#接受数据
	books_id = request.POST.get('books_id')

	#校验商品是否有效
	if not all([books_id]):
		return JsonResponse({'res':1,'errmas':'数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res':3,'errmsg':'商品不存在'})

	#删除购物车商品信息
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' %request.session.get('passport_id')
	conn.hdel(cart_key,books_id)
	#返回信息
	return JsonResponse({'res':3})



#前端传递过来的参数：商品id　books_id 更新数目　books_count
#post
#/cart/update/
#更改之后购物车的商品数目
def cart_update(request):
	'''更新购物车上品数目'''
	#判断用户是否的登陆
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登陆'})

	#接收数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')

	#数据的校验
	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	try:
		books_count = int(books_count)

	except Exception as e:
		return JsonResponse({'res':3,'errmsg':'商品数目必须为数字'})

	#更新操作
	conn = get_redis_connection('default')
	cart_key = 'cart_%d'%request.session.get('passport_id')

	#判断商品库存
	if books_count > books.stock:
		return JsonResponse({'res':4,'errmsg':'商品库存不足'})

	conn.hset(cart_key,books_id,books_count)
	return JsonResponse({'res':5})




























