from django.shortcuts import render
from .models import Comments
from django.http import JsonResponse
import json
# Create your views here.

def comment(request,book_id):
	#如果是get请求把评论内容取出传到前端渲染前端传过来bookid（查看评论）
	if request.method == 'GET':
		comments = Comments.objects.filter(book_id=book_id)
		res=[]
		for i in comments:
			res.append({
				'create_time':i.create_time,
				'user_id':i.user_id,
				'content':i.content
			})
		return	JsonResponse({
			'code':200,
			'data':res
		})
	#如果是post请求接受前端传来的信息存入数据库（写评论）
	elif request.method == 'POST':
		data = json.loads(request.body.decode('utf-8'))
		content = data.get('content')
		book_id = data.get('book_id')
		user_id = request.session.get('passport_id')
		c = Comments(content=content,books_id=book_id,passport_id=user_id)
		c.save()
		return JsonResponse({
			'code':200,
			'msg':'评论成功'

		})


