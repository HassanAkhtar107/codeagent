from django.contrib import admin
from .models import Project, ProjectFile


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "owner", "primary_language", "status", "is_public", "created_at"]
    list_filter = ["status", "primary_language", "is_public"]
    search_fields = ["name", "owner__username"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProjectFileInline]


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ["id", "project", "file_path", "language", "is_agent_generated", "updated_at"]
    list_filter = ["language", "is_agent_generated"]
    search_fields = ["file_path", "project__name"]
    readonly_fields = ["created_at", "updated_at"]
