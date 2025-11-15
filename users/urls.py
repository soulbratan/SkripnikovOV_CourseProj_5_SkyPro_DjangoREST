from django.urls import path
from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserRetrieveAPIView, UserListAPIView, UserUpdateAPIView, UserDestroyAPIView

app_name = UsersConfig.name

urlpatterns = [
    # users
    path("register/", UserCreateAPIView.as_view(), name="user-create"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-retrieve"),
    path("", UserListAPIView.as_view(), name="user-list"),
    path("<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
]