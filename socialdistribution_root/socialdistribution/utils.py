from django.http.request import HttpRequest
from rest_framework.serializers import ModelSerializer
from rest_framework.renderers import JSONRenderer

class Utils():
    @staticmethod
    def getAcceptedMediaType(request: HttpRequest):
        if (request.headers.__contains__("Accept")):
            return request.headers["Accept"]
        else:
            return "application/json"

    @staticmethod
    def serialize(serializer: ModelSerializer, request: HttpRequest):
        return JSONRenderer().render(serializer.data, Utils.getAcceptedMediaType(request))

    
    # Used for formatting and styling responses
    @staticmethod
    def formatResponse(query_type, data):
        json_result = {
            'query': query_type,
            'data': data
        }

        return json_result