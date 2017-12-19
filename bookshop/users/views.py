from django.http import JsonResponse
from django.shortcuts import render, redirect
from users.models import Passport
from django.core.urlresolvers import reverse
import re
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
#注册
@csrf_exempt
def register(request):
	if request.method == 'GET':
		return render(request, 'users/register.html')
	elif request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		email = request.POST.get('email')

		if not all([username,password,email]):
			#数据为空 1
			return JsonResponse({'res': 1})
		if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
			#邮箱格式不正确
			return JsonResponse({'res': 2})
		else:
			passport = Passport.objects.get_passport(username=username)
			if passport:
				#帐号被注册
				return JsonResponse({'res': 3})
			else:
				#写入数据库
				try:
					passport = Passport.objects.add_one_passport(username=username,password=password,email=email)
				except Exception as e:
					print(e)
				return JsonResponse({'res': 0})

#登陆
@csrf_exempt
def login(request):
	if request.method == 'GET':
		return render(request,'users/login.html')
	elif request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		remember = request.POST.get('remember')
		# print(username,password,remember)
		if not all([username,password]):
			#数据不能为空
			return JsonResponse({'res':0})
		else:
			passport = Passport.objects.get_one_passport(username=username,password=password)

			if passport:

				#登陆成功　写入session　记录用户登陆状态
				request.session['islogin'] = True
				request.session['username'] = username
				request.session['passport_id'] = passport.id

				jres = JsonResponse({'res':2})
				# 记住用户名
				if remember:
					jres.set_cookie('username',username,max_age=7*24*3600)
				else:
					jres.delete_cookie('uername')
				return jres
			else:
				#账户或密码不正确
				return JsonResponse({'res':1})

#退出
def logout(request):
	#清空用户信息
	request.session.flush()
	# 跳转到首页
	return redirect(reverse('books:index'))