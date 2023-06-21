import logging
import sqlite3
from sqlite3 import Error as sqliteError
from os.path import exists

from django.utils import timezone
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class PixelApiView(APIView):

    def __init__(self):
        super(PixelApiView, self).__init__()
        self.db_path = settings.DB_PATH
        self.conn = None

    def db_exists(self) -> bool:
        if exists(self.db_path):
            return True
        return False

    def create_db_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            self.conn = conn
        except sqliteError as ex:
            logging.error(ex)

    def update_opened_counter(self, receiver_email):
        last_opened = timezone.now().strftime("%d-%b-%Y %H:%M %p")
        sql = f"UPDATE emails SET email_opened='{True}', opened_counter=opened_counter+1, last_opened_at='{last_opened}' WHERE receiver_email='{receiver_email}'"
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def get(self, request):
        # EmailTracer.objects.insert(request.query_params.get('e', ''))
        try:
            if self.db_exists() is False:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            lead = request.query_params.get('e', '')
            if lead in ['', None]:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            self.create_db_connection()
            self.update_opened_counter(lead)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            logging.exception(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

# class OpenEmailTracerApiView(APIView):
#
#     def __init__(self):
#         super(OpenEmailTracerApiView, self).__init__()
#
#     @staticmethod
#     def get(request):
#         if request.headers.get('Secret', '') != settings.SECRET_KEY:
#             return Response(data='HTTP_401_UNAUTHORIZED', status=status.HTTP_401_UNAUTHORIZED)
#         data = EmailTracer.objects.get_total_opened()
#         return Response(data, status=status.HTTP_200_OK)
