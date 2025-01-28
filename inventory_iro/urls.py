from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include("home.urls")),
    path('administrator/', include("administrator.urls")),
    path('admin/', admin.site.urls),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG == False:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

