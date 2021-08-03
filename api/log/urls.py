from django.urls import path
from . import views

urlpatterns = [
    path('', views.LogAPI.as_view()),
]
