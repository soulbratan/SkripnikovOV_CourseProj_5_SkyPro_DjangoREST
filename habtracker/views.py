from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer, HabitCompletionSerializer
from .permissions import IsOwner
from .filters import HabitFilter


class HabitPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class HabitListCreateAPIView(generics.ListCreateAPIView):
    """Список и создание привычек текущего пользователя"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HabitFilter
    search_fields = ['place', 'action']
    ordering_fields = ['time', 'created_at']
    ordering = ['time']

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, обновление и удаление привычки"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_class = HabitFilter

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListAPIView(generics.ListAPIView):
    """Список публичных привычек"""

    serializer_class = PublicHabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HabitFilter
    search_fields = ['place', 'action', 'user__email']
    ordering_fields = ['time', 'created_at']

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)


class HabitCompletionCreateAPIView(generics.CreateAPIView):
    """Отметка выполнения привычки"""

    serializer_class = HabitCompletionSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        habit = self.get_object()
        serializer.save(habit=habit)