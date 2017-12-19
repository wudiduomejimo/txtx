from audioop import reverse

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from books.models import Books
from books.enumspy import *
# Create your views here.


def index(request):
	'''显示首页'''
	#查询每个种类的3个新品信息和4个销量最好的商品信息

	python_new = Books.objects.get_books_by_type(PYTHON,3,sort='new')
	python_hot = Books.objects.get_books_by_type(PYTHON,4,sort='hot')
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
	# 定义模板上下文
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
	return render(request,'books/index.html',context)

def detail(request,books_id):
	'''显示商品的详情页面'''
	#获取商品的详情页面
	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		#商品不存在
		return redirect(reverse('books:index'))
	#新品推荐
	books_li = Books.objects.get_books_by_type(type_id=books.type_id,limit=2,sort='new')
	#定义上下文
	context = {'books':books,'books_li':books_li}
	#使用模板
	return render(request,'books/detail.html',context)

#列表页
def list(request,type_id,page):
	'''商品列表页面'''
	#获取排序方式
	sort = request.GET.get('sort','default')
	#判断type_id是否合法
	if int(type_id) not in BOOKS_TYPE.keys():
		return redirect(reverse('books:index'))
	#根据商品种类id和排序方式查询数据库
	books_li = Books.objects.get_books_by_type(type_id=type_id,sort=sort)
	#分页
	paginator = Paginator(books_li,1)
	#获取分页之后的总页数
	num_pages = paginator.num_pages
	if page =='' or int(page) > num_pages:
		page = 1
	else:
		page = int(page)
	# 返回值是一个Page类的实例对象
	books_li = paginator.page(page)
	#返回值是一个paginator.page(page)
	#进行页码控制
	#小于５页全显示
	if num_pages < 5:
		pages = range(1,num_pages+1)
	elif num_pages < 3:
		pages = range(1,6)
	#后三页时显示５页
	elif num_pages-page <=2:
		pages = range(num_pages-4,num_pages+1)
	else:
		pages = range(num_pages-2,page+3)
	#新品推荐
	books_new = Books.objects.get_books_by_type(type_id=type_id,sort='new')
	# 定义上下文
	type_title = BOOKS_TYPE[int(type_id)]
	context = {
		'books_li': books_li,
		'books_new': books_new,
		'type_id': type_id,
		'sort': sort,
		'type_title': type_title,
		'pages': pages
	}
	print('sort',sort)
	return render(request,'books/list.html',context)



