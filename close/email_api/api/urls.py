from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
urlpatterns = [
    path("pixel", views.PixelApiView.as_view(), name='pixel_img_view'),
    path("open-counter", views.OpenEmailTracerApiView.as_view(), name='email_open_counter'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
