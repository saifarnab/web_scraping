"""
URL configuration for email_api project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # path("email-tracker/admin/", admin.site.urls),
    path('email/api/', include('api.urls'))
]

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
