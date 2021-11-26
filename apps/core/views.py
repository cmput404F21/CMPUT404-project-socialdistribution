from django.http.request import HttpRequest
from django.http.response import HttpResponseNotFound
from django.shortcuts import render
from django.urls.base import reverse
from django.views import generic
from .models import ExternalHost, User, Author, Follow
from .serializers import AuthorSerializer
from apps.posts.models import Post
from socialdistribution.utils import Utils
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

# Create your views here.
class IndexView(generic.TemplateView):
    template_name = 'core/index.html'

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", )

class SignUpView(generic.CreateView):
    form_class = RegisterForm
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse('login')

def followers(request: HttpRequest):
    if request.user.is_anonymous:
        return render(request,'core/index.html')
    currentAuthor=Author.objects.filter(userId=request.user).first()
    return followers_with_target(request, currentAuthor.id)


def followers_with_target(request: HttpRequest, author_id: str):
    host = Utils.getRequestHost(request)
    target_host = Utils.getUrlHost(author_id)
    followers = None
    followerUrl = author_id +"/followers"
    if (not target_host):
        followerUrl = host + "/author/" + author_id + "/followers"
    followers = Utils.getFromUrl(followerUrl)

    currentAuthor=Author.objects.filter(userId=request.user).first()
    if request.user.is_anonymous or (currentAuthor.id != author_id and not request.user.is_staff):
        return render(request,'core/index.html')
    
    target_author: dict = Utils.getAuthorDict(author_id, host)
    if (not target_author):
        return HttpResponseNotFound

    context = {
        'is_staff': request.user.is_staff,
        'author' : currentAuthor, 
        'authors': followers["data"] if followers and followers.__contains__("data") else [], 
        'host': host
    }
    return render(request, 'authors/followers.html', context)

def authors(request: HttpRequest):
    if request.user.is_anonymous:
        return render(request,'core/index.html')
    currentAuthor=Author.objects.filter(userId=request.user).first()

    target_host = request.GET.get('target_host', None)
    host = Utils.getRequestHost(request)
    authors = None
    if (not target_host or target_host == host):
        if (request.user.is_staff):
            authors = Author.objects.all()
        else:
            authors = Author.objects.filter(isApproved=True)
        serializer = AuthorSerializer(authors, context={'host': host}, many=True)
        authors = serializer.data
    else:
        authorUrl = target_host + "/authors"
        response = Utils.getFromUrl(authorUrl)
        if (response and response["data"]):
            authors = response["data"]
        else:
            return HttpResponseNotFound

    hosts = list(ExternalHost.objects.values_list('host', flat=True))
    if (not host in hosts):
        hosts.append(host)
    context = {
        'is_staff': request.user.is_staff,
        'author' : currentAuthor, 
        'authors': authors, 
        'host': host,
        'hosts': hosts,
        'selected_host': target_host if target_host else host,
    }
    return render(request, 'authors/index.html', context)

def author(request: HttpRequest, author_id: str):
    currentAuthor=Author.objects.filter(userId=request.user).first()
    
    if request.user.is_anonymous:
        return render(request,'core/index.html')
    
    is_following = False
    try:
        follow = Follow.objects.get(follower_id=currentAuthor.id, target_id = author_id)
        if (follow):
            is_following = True
    except:
        is_following = False

    host = request.scheme + "://" + request.get_host()
    context = {
        'author' : currentAuthor, 
        'author_id': currentAuthor.id,
        'is_staff': request.user.is_staff,
        'target_author_id' : author_id,
        'host':host,
        'is_following': is_following
    }
    return render(request,'authors/author.html',context)

# def author(request: HttpRequest):
#     host = Utils.getRequestHost(request)
#     author_id = request.GET.get('author_id', None)
#     if (not author_id):
#         return redirect(reverse('core:authors'))

#     author_id = Utils.cleanAuthorId(author_id, host)
#     currentAuthor=Author.objects.filter(userId=request.user).first()
#     if request.user.is_anonymous or (currentAuthor.id != author_id and not request.user.is_staff):
#         return render(request,'core/index.html')
    
#     target_author: dict = Utils.getAuthorDict(author_id, host)
#     if (not target_author):
#         return HttpResponseNotFound

#     is_following = False
#     try:
#         follow = Follow.objects.get(follower_id=currentAuthor.id, target_id = author_id)
#         if (follow):
#             is_following = True
#     except:
#         is_following = False

#     host = request.scheme + "://" + request.get_host()
#     context = {
#         'host':host,
#         'author': AuthorSerializer(currentAuthor, context={'host': host}).data,
#         'is_staff': request.user.is_staff,
#         'target_author' : target_author,
#         'is_following': is_following
#     }
#     return render(request,'authors/author.html',context)