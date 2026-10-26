from django.contrib import admin
from .models import CodeRun


@admin.register(CodeRun)
class CodeRunAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "language", "status", "exit_code", "duration_ms", "created_at"]
    list_filter = ["language", "status"]
    search_fields = ["user__username"]
    readonly_fields = ["stdout", "stderr", "exit_code", "status", "duration_ms", "created_at"]
