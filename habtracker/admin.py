from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """Настройки АДМИНКИ для привычек"""
    list_display = ("id", "user", "action", "place", "time", "frequency", "is_pleasant", "is_public")
    list_filter = ("is_pleasant", "is_public", "frequency", "created_at")
    search_fields = ("action", "place", "user__email")
    readonly_fields = ("created_at",)
