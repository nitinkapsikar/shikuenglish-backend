from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("day", "step", "message")
    list_filter = ("day",)
    search_fields = ("message",)
    ordering = ("day", "step")