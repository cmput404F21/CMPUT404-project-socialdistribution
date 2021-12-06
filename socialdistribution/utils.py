from re import search
from django.http.request import HttpRequest
from django.http.response import Http404
from requests.models import HTTPBasicAuth, Response
from rest_framework.renderers import JSONRenderer
from apps.core.models import Author, ExternalHost, Settings
from apps.posts.models import Comment
from apps.posts.serializers import CommentSerializer
from apps.core.serializers import AuthorSerializer
import requests
from base64 import b64encode
from django.shortcuts import render

class Utils():
    @staticmethod
    def getAcceptedMediaType(request: HttpRequest):
        if (request.headers.__contains__("Accept")):
            return request.headers["Accept"]
        else:
            return "application/json"

    @staticmethod
    def serialize(data: dict, request: HttpRequest):
        media = Utils.getAcceptedMediaType(request)
        return JSONRenderer().render(data, media)

    @staticmethod
    def getUrlHost(url: str, replaceLocal: bool = True):
        res = search('^(?P<scheme>[^:]*)://(?P<host>[^/]*)', url)
        if (res and res.group and res.group('scheme') and res.group('host')):
            scheme = res.group('scheme')
            host = res.group('host')
            if (replaceLocal):
                res2 = search('^127.0.0.1:(?P<port>.*)', host)
                if (res2 and res2.group and res2.group('port')):
                    host = "localhost:" + res2.group('port')
            return scheme + "://" + host
        return None

    @staticmethod
    def getRequestHost(request: HttpRequest):
        return request.scheme + "://" + request.get_host()

    @staticmethod
    def isLocalId(id, host):
        id_host = Utils.getUrlHost(id)
        if (id_host and Utils.areSameHost(id_host, host)):
            return True
        return False

    @staticmethod
    def areSameHost(host1, host2):
        res = search('^(?P<scheme>.*)://127.0.0.1:(?P<port>[^/]*)', host1)
        if (res and res.group and res.group('scheme') and res.group('port')):
            host1 = res.group('scheme') + "://localhost:" + res.group('port')
        res2 = search('^(?P<scheme>.*)://127.0.0.1:(?P<port>[^/]*)', host2)
        if (res2 and res2.group and res2.group('scheme') and res2.group('port')):
            host2 = res2.group('scheme') + "://localhost:" + res2.group('port')
        return host1 == host2

    @staticmethod
    def cleanAuthorId(id: str, host: str):
        id_host = Utils.getUrlHost(id)
        if (id_host and Utils.areSameHost(id_host, host)):
            return Utils.getAuthorId(id)
        return id

    @staticmethod
    def cleanCommentId(id: str, host: str):
        id_host = Utils.getUrlHost(id)
        if (id_host and Utils.areSameHost(id_host, host)):
            return Utils.getCommentId(id)
        return id

    @staticmethod
    def cleanPostId(id: str, host: str):
        id_host = Utils.getUrlHost(id)
        if (id_host and Utils.areSameHost(id_host, host)):
            return Utils.getPostId(id)
        return id
    
    # Helper function with error checking to get Author object from id
    @staticmethod
    def getAuthorDict(author_id: str, host:str, allowExternal: bool = True) -> dict:
        try:
            author = Author.objects.get(pk=author_id)
            if (author):
                serializer = AuthorSerializer(author, context={'host': host})
                return serializer.data
        except Author.DoesNotExist:
            if (allowExternal):
                response = Utils.getFromUrl(author_id)
                if (response.__contains__("data")):
                    if (hasattr(response["data"], '__len__') and len(response["data"]) > 0):
                        response = response["data"][0]
                    else:
                        response = response["data"]

                if (response.__contains__("url")):
                    response["id"] = response["url"]

                return response
        raise Http404()

    # Helper function with error checking to get Author object from id
    @staticmethod
    def getCommentDict(comment_id: str, host:str, allowExternal: bool = True) -> dict:
        id_host = Utils.getUrlHost(comment_id)
        if (id_host and id_host != host and allowExternal):
            return Utils.getFromUrl(comment_id)

        try:
            comment = Comment.objects.get(pk=comment_id)
            if (comment):
                serializer = CommentSerializer(comment, context={'host': host})
                return serializer.data
        except Author.DoesNotExist:
            raise Http404()
        raise Http404()

    @staticmethod
    def getAuthor(author_id: str) -> Author:
        try:
            return Author.objects.get(pk=author_id)
        except Author.DoesNotExist:
            raise Http404()

    @staticmethod
    def getAuthorId(url:str):
        """ 
        Returns an id of a proper athor entity, None otherwise
        """
        res = search('author(s?)/(?P<id>[^/]*)(/)?$', url)
        if (res and res.group and res.group('id')):
            return res.group('id')
        return None
    
    @staticmethod
    def getPostId(url:str):
        """ 
        Returns an id of a proper post entity, None otherwise
        """
        res = search('post(s?)/(?P<id>[^/]*)(/)?$', url)
        if (res and res.group and res.group('id')):
            return res.group('id')
        return None

    @staticmethod
    def getCommentId(url:str):
        """ 
        Returns an id of a proper comment entity, None otherwise
        """
        res = search('comment(s?)/(?P<id>[^/]*)(/)?$', url)
        if (res and res.group and res.group('id')):
            return res.group('id')
        return None

    @staticmethod
    def extractPostId(url:str):
        """ 
        Returns an id of a post from any uri matching syntax "posts?/id(/any)?", None otherwise
        """
        res = search('post(s?)/(?P<id>[^/]*)(/.*)?$', url)
        if (res and res.group and res.group('id')):
            return res.group('id')
        return None
    
    @staticmethod
    def getFromUrl(url:str) -> Response:
        host = Utils.getUrlHost(url, False)
        try:
            externalHost = ExternalHost.objects.get(host__startswith=host)
        except:
            raise Http404()
        
        response = None
        if (externalHost):
            if externalHost.username and externalHost.password:
                response = requests.get(url, auth=HTTPBasicAuth(username=externalHost.username, password=externalHost.password))
            elif externalHost.token:
                headers = { 'Authorization' : 'Basic %s' %  externalHost.token }
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url)

            if (response.status_code < 200 or response.status_code > 299):
                raise Http404()
            return response.json()
            
        raise Http404()

    @staticmethod
    def deleteFromUrl(url:str) -> Response:
        host = Utils.getUrlHost(url, False)
        try:
            externalHost = ExternalHost.objects.get(host__startswith=host)
        except:
            raise Http404()
        
        response = None
        if (externalHost):
            if externalHost.username and externalHost.password:
                response = requests.delete(url, auth=HTTPBasicAuth(username=externalHost.username, password=externalHost.password))
            elif externalHost.token:
                headers = { 'Authorization' : 'Basic %s' %  externalHost.token }
                response = requests.delete(url, headers=headers)
            else:
                response = requests.delete(url)

            if (response.status_code < 200 or response.status_code > 299):
                raise Http404()
            return response.content
            
        raise Http404()
    
    @staticmethod
    def postToUrl(url:str, data: dict) -> Response:
        host = Utils.getUrlHost(url, False)
        try:
            externalHost = ExternalHost.objects.get(host__startswith=host)
        except:
            raise Http404()
        
        response = None
        if (externalHost):
            if externalHost.username and externalHost.password:
                response = requests.post(url, json=data, auth=HTTPBasicAuth(username=externalHost.username, password=externalHost.password))
            elif externalHost.token:
                headers = { 'Authorization' : 'Basic %s' %  externalHost.token }
                response = requests.post(url, json=data, headers=headers)
            else:
                response = requests.post(url, json=data)

            if (response.status_code < 200 or response.status_code > 299):
                raise Http404()
            return response.json()
            
        raise Http404()

    # Used for formatting and styling responses
    @staticmethod
    def formatResponse(query_type, data, obj_type=None):
        if obj_type is not None:
            json_result = {
                'query': query_type,
                'type': obj_type,
                'data': data
            }
        else:
            json_result = {
                'query': query_type,
                'data': data
            }
            

        return json_result

    @staticmethod
    def requiresApproval():
        try: 
            return Settings.objects.get(pk="RequireApproval").value == "True"
        except:
            return False

    @staticmethod
    def allowsSignUp():
        try: 
            return Settings.objects.get(pk="AllowSignUp").value == "True"
        except:
            return False

    def defaultRender(request: HttpRequest, template_name, context = {}):
        context['allowSignUp'] = Utils.allowsSignUp()
        context['requireApproval'] = Utils.requiresApproval()
        context['is_staff'] = False if request.user.is_anonymous else request.user.is_staff 
        return render(request, template_name, context)