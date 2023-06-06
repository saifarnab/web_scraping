from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
urlpatterns = [
    path("fake_img", views.FakeImgApiView.as_view(), name='fake_img_view'),
    path("open-counter", views.OpenEmailTracerApiView.as_view(), name='email_open_counter'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
