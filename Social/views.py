from django.http import JsonResponse
from django.shortcuts import render
from .models import User, Post, Comment
# Create your views here.


def getUserInfo(request,username):
    try:
        user = User.objects.get(username=username)
        posts = user.posts.all().values('id', 'content', 'created_at', 'updated_at', 'media')
        # Convert the posts QuerySet to a list to make it serializable
        posts_list = list(posts)
        return JsonResponse({"posts": posts_list})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
