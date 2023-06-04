from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
urlpatterns = [
    path("fake_img", views.PixelImgApiView.as_view(), name='fake_img_view'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
