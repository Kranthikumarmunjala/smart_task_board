from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'estimated_time', 'is_completed', 'is_locked', 'created_at')
    list_filter = ('priority', 'is_completed', 'is_locked', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'priority', 'estimated_time')
        }),
        ('Status', {
            'fields': ('is_completed', 'is_locked')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )