from django.http import JsonResponse
from django.shortcuts import render
from users.models import Passport
from django.views.decorators.csrf import csrf_exempt
import re

# Create your views here.
@csrf_exempt
def register(request):
	if request.method == 'GET':
		return render(request, 'users/register.html')
	elif request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		email = request.POST.get('email')
		print(username,password,email)
		if not all [username,password,email]:
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
				passport = Passport.objects.add_one_passport(username=username,password=password,email=email)
				return JsonResponse({'res': 0})


def login(request):
	return render(request,'users/login.html')