from django.contrib import admin
from django.urls import path, include
from myapp import urls as myapp_urls



from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include((myapp_urls, 'myapp'), namespace='myapp')),  # Передаем кортеж
    path('accounts/', include('django.contrib.auth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
