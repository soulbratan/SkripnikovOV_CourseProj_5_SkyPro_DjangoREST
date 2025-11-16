from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Habit
from .serializers import (
    HabitSerializer,
    PublicHabitSerializer,
    HabitCreateSerializer,
    HabitListSerializer
)
from users.permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычек"""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """Возвращает привычки текущего пользователя"""
        if self.action == 'public':
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return HabitCreateSerializer
        elif self.action == 'list':
            return HabitListSerializer
        elif self.action == 'public':
            return PublicHabitSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        """Создание привычки с текущим пользователем в качестве владельца"""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def public(self, request):
        """Список публичных привычек"""
        habits = self.get_queryset()
        page = self.paginate_queryset(habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Отметить привычку как выполненную"""
        habit = self.get_object()
        habit.mark_completed()
        return Response(
            {'status': 'Привычка отмечена как выполненная', 'completed_at': habit.last_completed},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Предстоящие привычки (на сегодня)"""
        from django.utils import timezone
        from datetime import datetime, timedelta

        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        habits = self.get_queryset().filter(
            time__date=today
        ).order_by('time')

        page = self.paginate_queryset(habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)


class MyHabitViewSet(viewsets.ModelViewSet):
    """ViewSet только для привычек текущего пользователя"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
