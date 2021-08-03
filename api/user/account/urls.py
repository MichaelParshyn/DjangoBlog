from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountAPI.as_view()),
    path('<int:pk>', views.AccountAPI.as_view()),
]