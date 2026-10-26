"""
code_agent_core URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("code_agent_core.api_router")),
]

try:
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    api_info = openapi.Info(
        title="Code Agent API",
        default_version="v1",
        description="Full API documentation for the Code Agent Platform — AI-powered coding assistant.",
    )

    schema_view = get_schema_view(
        api_info,
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [
        path("api-docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api_docs")
    ]
except Exception:
    pass

admin.site.site_header = "Code Agent Admin"
admin.site.site_title = "Code Agent Portal"
admin.site.index_title = "Code Agent Administration"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
