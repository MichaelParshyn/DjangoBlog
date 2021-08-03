from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .user import views

urlpatterns = [
    path('log/', include('api.log.urls')),
    path('post/', include('api.post.urls')),
    path('user/', include('api.user.urls')),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
]