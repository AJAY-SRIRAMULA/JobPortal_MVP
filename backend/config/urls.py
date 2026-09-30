from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from api.views import LoginView, RegisterView
urlpatterns=[path('admin/',admin.site.urls),path('api/auth/register/',RegisterView.as_view()),path('api/auth/login/',LoginView.as_view()),path('api/auth/refresh/',TokenRefreshView.as_view()),path('api/',include('api.urls'))] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
