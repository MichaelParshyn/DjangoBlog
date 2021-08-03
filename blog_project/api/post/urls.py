from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostAPI.as_view()),
    path('<int:pk>', views.PostAPI.as_view()),
    path('react', views.PostAPI.react, name='react on post'),
    path('reaction-stat', views.PostAPI.get_reaction_stat, name='get reaction statistic'),
]