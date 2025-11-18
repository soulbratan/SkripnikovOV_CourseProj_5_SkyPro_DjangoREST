from django.urls import path
from habtracker.apps import HabtrackerConfig
from . import views

app_name = HabtrackerConfig.name

urlpatterns = [
    path("", views.HabitListCreateAPIView.as_view(), name="habit-list-create"),
    path("<int:pk>/", views.HabitRetrieveUpdateDestroyAPIView.as_view(), name="habit-detail"),
    path("public/", views.PublicHabitListAPIView.as_view(), name="public-habits"),
    path("<int:pk>/complete/", views.HabitCompletionCreateAPIView.as_view(), name="habit-complete"),
]
