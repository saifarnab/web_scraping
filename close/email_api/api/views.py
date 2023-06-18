import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailTracer

logger = logging.getLogger(__name__)


class PixelApiView(APIView):

    def __init__(self):
        super(PixelApiView, self).__init__()

    @staticmethod
    def get(request):
        EmailTracer.objects.insert(request.query_params.get('e', ''))
        return Response(status=status.HTTP_200_OK)


class OpenEmailTracerApiView(APIView):

    def __init__(self):
        super(OpenEmailTracerApiView, self).__init__()

    @staticmethod
    def get(request):
        if request.headers.get('Secret', '') != settings.SECRET_KEY:
            return Response(data='HTTP_401_UNAUTHORIZED', status=status.HTTP_401_UNAUTHORIZED)
        data = EmailTracer.objects.get_total_opened()
        return Response(data, status=status.HTTP_200_OK)
