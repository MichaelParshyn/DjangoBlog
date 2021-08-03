from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from . import views

urlpatterns = [
    path('', views.UserAPI.as_view()),
    path('<int:pk>', views.UserAPI.as_view()),
    path('account/', include('api.user.account.urls')),
    path('login/', TokenObtainPairView.as_view()),
    path('register/', views.UserAPI.as_view()),
]