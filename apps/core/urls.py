from django.urls import path
from django.urls.conf import re_path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('index', views.IndexView.as_view(), name='index'),
    path('site/accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('site/authors', views.authors, name='authors'),
    path('site/authors/followers/', views.followers, name='followers'),
    path('site/authors/<path:author_id>/followers', views.followers_with_target, name='followers_with_target'),
    path('site/authors/<path:author_id>', views.author, name='author'),
    path('site/friend_requests/', views.friend_requests, name='friend_requests'),
    # path('site/authors', views.authors.as_view(), name='authors'),
    # path("site/authors/<str:author_id>/followers", views.FollowerDetails.as_view(), name="author-followers"),
    # path("site/authors/<str:author_id>/followers/<str:foreign_author_id>", views.FollowerDetails.as_view(), name="follower-info"),
]