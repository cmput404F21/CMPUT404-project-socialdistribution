from django.urls import path

from . import views

app_name = 'author'
urlpatterns = [
    path('authors', views.authors.as_view(), name='authors'),
    path("author/<path:author_id>/followers/<path:foreign_author_id>", views.FollowerDetails.as_view(), name="follower-info"),
    path("author/<path:author_id>/followers", views.FollowerDetails.as_view(), name="author-followers"),
    path('author/<path:author_id>', views.author.as_view(), name='author'),
]