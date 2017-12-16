from django.shortcuts import render,redirect
from django_redis import get_redis_connection
from books.models import Books
from books.enums import *
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page #redis

# Create your views here.
#设置时间(60 * 15)
# @cache_page(60 * 15)
def index(request):
	'''显示首页'''
	#查询出每个种类的3个新品信息和４个销量最好的商品信息
	# python_new = Books.objects.filter(type_id=1).order_by('price')[:3]
	# python_hot = Books.objects.filter(type_id=1).order_by('-sales')[:4]
	# javascript_new = Books.objects.filter(type_id=2).order_by('price')[:3]
	# javascript_hot = Books.objects.filter(type_id=2).order_by('-sales')[:4]
	# algorithms_new = Books.objects.filter(type_id=3).order_by('price')[:3]
	# algorithms_hot = Books.objects.filter(type_id=3).order_by('-sales')[:4]
	# machinelearning_new = Books.objects.filter(type_id=4).order_by('price')[:3]
	# machinelearning_hot = Books.objects.filter(type_id=4).order_by('-sales')[:4]
	# operatingsystem_new = Books.objects.filter(type_id=5).order_by('price')[:3]
	# operatingsystem_hot = Books.objects.filter(type_id=5).order_by('-sales')[:4]
	# database_new = Books.objects.filter(type_id=6).order_by('price')[:3]
	# database_hot = Books.objects.filter(type_id=6).order_by('-sales')[:4]
	python_new = Books.objects.get_books_by_type(PYTHON, 3, sort='new')
	python_hot = Books.objects.get_books_by_type(PYTHON, 4, sort='hot')
	javascript_new = Books.objects.get_books_by_type(JAVASCRIPT, 3, sort='new')
	javascript_hot = Books.objects.get_books_by_type(JAVASCRIPT, 4, sort='hot')
	algorithms_new = Books.objects.get_books_by_type(ALGORITHMS, 3, sort='new')
	algorithms_hot = Books.objects.get_books_by_type(ALGORITHMS, 4, sort='hot')
	machinelearning_new = Books.objects.get_books_by_type(MACHINELEARNING, 3, sort='new')
	machinelearning_hot = Books.objects.get_books_by_type(MACHINELEARNING, 4, sort='hot')
	operatingsystem_new = Books.objects.get_books_by_type(OPERATINGSYSTEM, 3, sort='new')
	operatingsystem_hot = Books.objects.get_books_by_type(OPERATINGSYSTEM, 4, sort='hot')
	database_new = Books.objects.get_books_by_type(DATABASE, 3, sort='new')
	database_hot = Books.objects.get_books_by_type(DATABASE, 4, sort='hot')

	context = {
		'python_new': python_new,
		'python_hot': python_hot,
		'javascript_new': javascript_new,
		'javascript_hot': javascript_hot,
		'algorithms_new': algorithms_new,
		'algorithms_hot': algorithms_hot,
		'machinelearning_new': machinelearning_new,
		'machinelearning_hot': machinelearning_hot,
		'operatingsystem_new': operatingsystem_new,
		'operatingsystem_hot': operatingsystem_hot,
		'database_new': database_new,
		'database_hot': database_hot,
	}
	# 使用模板
	return render(request,'books/index.html',context)


def detail(request,books_id):
	'''显示商品的详情页'''
	#获取商品的详情页面
	books = Books.objects.get_books_by_id(books_id=books_id)
	#商品不存在跳转index页面
	if books is None:
		return redirect(reverse('books:index'))
	#新品推荐
	books_li = Books.objects.filter(type_id=books.type_id).order_by('-sales')[:4]
	#登入时写入session   request.session['islogin'] = True
	if request.session.has_key('islogin'):
		#用户已经注册记录浏览信息
		con = get_redis_connection('default')
		key = 'history_%d'%request.session.get('passport_id')
		#先从redis中移除books.id

		con.lrem(key,0,books.id)
		# 保存最近浏览的５个商品
		con.lpush(key,books_id)
		# 保存用户最近浏览的5个商品
		con.ltrim(key, 0, 4)

	#定义上下文
	context = {'books':books,"books_li":books_li}
	return render(request,'books/detail.html',context)


#列表页
def list(request,type_id,page):
	'''商品列表页'''
	#获取排序方式
	sort = request.GET.get('sort','default')#get获取
	#判断type_id是否合法
	if int(type_id) not in BOOKS_TYPE.keys():
		return redirect(reverse('books:index'))

	#根据商品种类id和排序方式查询数据
	books_li = Books.objects.get_books_by_type(type_id=type_id,sort=sort)
	#分页
	paginator = Paginator(books_li,1)
	#总页数
	num_pages = paginator.num_pages

	if page == '' or int(page) > num_pages:
		page = 1
	else:
		page = int(page)
	#返回值是一个page类的实例对象(具体页的数据列表)
	books_li = paginator.page(page)

	# 进行页码控制
	# 1.总页数<5, 显示所有页码
	# 2.当前页是前3页，显示1-5页
	# 3.当前页是后3页，显示后5页 10 9 8 7
	# 4.其他情况，显示当前页前2页，后2页，当前页
	if num_pages < 5:
		pages = range(1,num_pages+1)
	elif num_pages <=3:
		pages = range(1,6)
	elif num_pages - page <= 2:
		pages = range(num_pages-4,num_pages+1)
	else:
		pages = range(page-2,page+3)

	#新品推荐

	books_new = Books.objects.filter(type_id=type_id).order_by('-sales')
	#定义上下文
	type_title = BOOKS_TYPE[int(type_id)]
	context = {

		'books_li': books_li,
		'books_new':books_new,
		'type_id':type_id,
		'sort':sort,
		type_title:type_title,
		'pages':pages

	}
	return render(request,'books/list.html',context)




