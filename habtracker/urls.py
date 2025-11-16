from django.urls import path
from habtracker.apps import HabtrackerConfig
from . import views

app_name = HabtrackerConfig.name

urlpatterns = [
    path('habits/', views.HabitListCreateAPIView.as_view(), name='habit-list-create'),
    path('habits/<int:pk>/', views.HabitRetrieveUpdateDestroyAPIView.as_view(), name='habit-detail'),
    path('habits/public/', views.PublicHabitListAPIView.as_view(), name='public-habits'),
]
