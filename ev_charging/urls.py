from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("charging_station.urls")),
    path('', include("VoltHub.urls")),
    path('', include("authentication.urls")),
    #authentication
    path('auth', include('authentication.urls')),
    #ecommerce
    path('ecommerce/', include('ecommerce.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
