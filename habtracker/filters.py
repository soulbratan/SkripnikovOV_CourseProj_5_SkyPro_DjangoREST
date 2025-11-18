import django_filters
from .models import Habit


class HabitFilter(django_filters.FilterSet):
    place = django_filters.CharFilter(lookup_expr="icontains", label="Место")
    action = django_filters.CharFilter(lookup_expr="icontains", label="Действие")
    is_pleasant = django_filters.BooleanFilter(label="Приятная привычка")
    is_public = django_filters.BooleanFilter(label="Публичная")

    class Meta:
        model = Habit
        fields = ["place", "action", "is_pleasant", "is_public", "frequency"]