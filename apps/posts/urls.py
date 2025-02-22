from django.urls import path

from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.index, name='index'),
    path('my_posts/', views.my_posts, name='my_posts'),
    path('friend_posts/', views.friend_posts, name='friend_posts'),
    path('my_github_feed/',views.github,name="my_github_feed"),
    path('my_posts/<path:post_id>/', views.postdetails, name='postdetails'),
    path('makepost/', views.makepost,name='makepost'),
    path('editpost/<str:post_id>/', views.editpost, name='editpost'),
    path('deletepost/<str:post_id>/', views.deletepost, name='deletepost'),
    path('<path:post_id>/', views.postdetails, name='postdetails'),
]