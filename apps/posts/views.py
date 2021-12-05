from django.shortcuts import render, redirect, get_object_or_404
from django.http.request import HttpRequest
from django.core.paginator import Paginator

from .models import Post, Like, Comment
from apps.core.models import Author
from socialdistribution.utils import Utils
from socialdistribution.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE


def index(request: HttpRequest):
    # should include friends etc at some points
    posts = Post.objects.filter(unlisted=False, visibility="PUBLIC")

    request_data = request.GET
    request_page = request_data.get("page", DEFAULT_PAGE)
    request_size = request_data.get("size", DEFAULT_PAGE_SIZE)

    paginator = Paginator(posts, request_size)
    try:
        posts_page = paginator.page(request_page)
    except:
        posts_page = []
    abs_path_no_query = request.build_absolute_uri(request.path)

    next_page = None
    if (posts_page != [] and posts_page.has_next()):
        next_page = posts_page.next_page_number()
    prev_page = None
    if (posts_page != [] and posts_page.has_previous()):
        prev_page = posts_page.previous_page_number()

    for post in posts_page:
        post.comments_top3 = get_3latest_comments(post.id)
        post.num_likes = len(get_likes_post(post.id))

    host = request.scheme + "://" + request.get_host()
    context = {
        'posts': posts_page,
        'host': host,
        'request_next_page': next_page,
        'request_next_page_link': abs_path_no_query + "?page=" + str(next_page) + "&size=" + str(request_size),
        'request_prev_page': prev_page,
        'request_prev_page_link': abs_path_no_query + "?page=" + str(prev_page) + "&size=" + str(request_size),
        'request_size': request_size
        }
    if request.user.is_anonymous or not (request.user.is_authenticated):
        return render(request,'posts/index.html',context)
    
    context['author']=Author.objects.filter(userId=request.user).first()
    return render(request, 'posts/index.html', context)

def my_posts(request: HttpRequest):
    if request.user.is_anonymous or not (request.user.is_authenticated):
        return render(request,'posts/index.html')

    currentAuthor = Author.objects.get(userId=request.user)
    posts = Post.objects.filter(author=currentAuthor)

    request_data = request.GET
    request_page = request_data.get("page", DEFAULT_PAGE)
    request_size = request_data.get("size", DEFAULT_PAGE_SIZE)

    paginator = Paginator(posts, request_size)
    try:
        posts_page = paginator.page(request_page)
    except:
        posts_page = []
    abs_path_no_query = request.build_absolute_uri(request.path)

    next_page = None
    if (posts_page != [] and posts_page.has_next()):
        next_page = posts_page.next_page_number()
    prev_page = None
    if (posts_page != [] and posts_page.has_previous()):
        prev_page = posts_page.previous_page_number()

    for post in posts_page:
        post.comments_top3 = get_3latest_comments(post.id)
        post.num_likes = len(get_likes_post(post.id))

    host = request.scheme + "://" + request.get_host()
    context = {
        'posts': posts_page,
        'host': host,
        'request_next_page': next_page,
        'request_next_page_link': abs_path_no_query + "?page=" + str(next_page) + "&size=" + str(request_size),
        'request_prev_page': prev_page,
        'request_prev_page_link': abs_path_no_query + "?page=" + str(prev_page) + "&size=" + str(request_size),
        'request_size': request_size,
        'userAuthor': currentAuthor
        }
    return render(request, 'posts/index.html', context)

def makepost(request: HttpRequest):
    if request.user.is_anonymous or not (request.user.is_authenticated):
        return render(request,'posts/makepost.html')

    currentAuthor = Author.objects.filter(userId=request.user).first()
    host = request.scheme + "://" + request.get_host()
    context = {'author' : currentAuthor, 'host' : host}
    return render(request,'posts/makepost.html',context)

def postdetails(request: HttpRequest, post_id):
    if request.user.is_anonymous:
        return render(request,'core/index.html')

    currentAuthor = Author.objects.get(userId=request.user)
    host = Utils.getRequestHost(request)
    post_id = Utils.cleanPostId(post_id, host)
    print(post_id)
    target_host = Utils.getUrlHost(post_id)
    if (not target_host or Utils.areSameHost(target_host, host)):
        target_host = host
    comments = None
    postLikes= None
    num_post_likes = None
    posts = None
    if target_host == host:
        post = get_object_or_404(Post, id=post_id)
        post.num_likes = len(get_likes_post(post.id))
        comments = get_comments(post.id)
    else:
        post_resp = Utils.getFromUrl(post_id)
        post = None
        if (post_resp.__contains__("data")):
            post = post_resp["data"]
            # TODO This probably needs more for the foreign host
        comments = []

    request_data = request.GET
    request_page = request_data.get("page", DEFAULT_PAGE)
    request_size = request_data.get("size", DEFAULT_PAGE_SIZE)

    paginator = Paginator(comments, request_size)
    try:
        comments_page = paginator.page(request_page)
    except:
        comments_page = []
    abs_path_no_query = request.build_absolute_uri(request.path)

    next_page = None
    if (comments_page != [] and comments_page.has_next()):
        next_page = comments_page.next_page_number()
    prev_page = None
    if (comments_page != [] and comments_page.has_previous()):
        prev_page = comments_page.previous_page_number()
    
    post.page_comments = comments_page

    context = {
        'post': post,
        'host': host,
        'request_next_page': next_page,
        'request_next_page_link': abs_path_no_query + "?page=" + str(next_page) + "&size=" + str(request_size),
        'request_prev_page': prev_page,
        'request_prev_page_link': abs_path_no_query + "?page=" + str(prev_page) + "&size=" + str(request_size),
        'request_size': request_size,
        'userAuthor': currentAuthor
        }
    return render(request, 'posts/postdetails.html', context)


def editpost(request: HttpRequest, post_id: str):
    if request.user.is_anonymous or not (request.user.is_authenticated):
        return render(request,'posts/editpost.html')

    currentAuthor=Author.objects.filter(userId=request.user).first()
    post = Post.objects.get(pk=post_id)
    host = request.scheme + "://" + request.get_host()
    context = {'author' : currentAuthor, 'post': post, 'host':host}
    return render(request,'posts/editpost.html',context)

def deletepost(request: HttpRequest, post_id: str):
    if request.user.is_anonymous or not (request.user.is_authenticated):
        return render(request,'posts/index.html')
    currentAuthor=Author.objects.filter(userId=request.user).first()
    post = Post.objects.get(pk=post_id)
    if post.author.id == currentAuthor.id:
        post.delete()
    return redirect('posts:index')

def get_3latest_comments(post_id):
    comments = Comment.objects.filter(post=post_id)[:3]
    return comments

def get_comments(post_id):
    comments = Comment.objects.filter(post=post_id)
    return comments

def get_likes_post(post_id):
    likes = Like.objects.filter(post=post_id)
    return likes
