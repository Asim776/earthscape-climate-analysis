from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/ingestion/', include('data_ingestion.urls')),
    path('api/processing/', include('data_processing.urls')),
    path('api/ml/', include('ml_models.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]
