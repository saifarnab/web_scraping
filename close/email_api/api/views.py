import logging
import pytracking

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class PixelImgApiView(APIView):

    def __init__(self):
        super(PixelImgApiView, self).__init__()
        self.lang = 'en'

    def get(self, request):

        print('hit')

        return Response(
            {
                'code': str(status.HTTP_200_OK),
                'lang': self.lang,
                'message': 'success',
                'data': {'url': 'https://'}
            }
        )
