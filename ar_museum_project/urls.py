from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from artifacts.views import AdminLogsView

urlpatterns = [
    path('admin/logs/', AdminLogsView.as_view(), name='admin_logs'),
    path('admin/', admin.site.urls),
    path('', include('artifacts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
