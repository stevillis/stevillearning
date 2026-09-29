"""Admin configuration for the models."""

from django.contrib import admin, messages

from learning_hub.models import Category, Certification, Course, Formation, Institution
from learning_hub.services.webhook_service import build_payload, send_webhook


def custom_titled_filter(title):
    """Creates a custom titled filter for admin list filters."""

    class Wrapper(admin.FieldListFilter):
        """Wrapper class to set a custom title for the filter."""

        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


@admin.action(description="Sync selected items to stevillis.com.br (RAG)")
def sync_selected_to_rag(modeladmin, request, queryset):
    """Admin action to trigger manual RAG sync for selected items."""
    success_count = 0
    failure_count = 0
    for item in queryset:
        action = "delete" if getattr(item, "is_active", True) is False else "upsert"
        payload = build_payload(item, action=action)
        if send_webhook(payload):
            success_count += 1
        else:
            failure_count += 1

    if success_count > 0:
        messages.success(request, f"Successfully triggered sync for {success_count} item(s).")
    if failure_count > 0:
        messages.warning(
            request,
            f"Failed to sync {failure_count} item(s). Check server logs and webhook configuration.",
        )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""

    fields = ["name"]
    list_display = (
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """Admin configuration for Institution model."""

    fields = ["name"]
    list_display = (
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    """Admin configuration for Formation model."""

    fields = ["name", "workload", "description", "start_date", "end_date"]
    list_display = (
        "name",
        "workload",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
    )
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin configuration for Course model."""

    fields = [
        "name",
        "workload",
        "description",
        "curriculum_map",
        "start_date",
        "end_date",
        "institution",
        "categories",
        "formation",
        "is_active",
    ]
    list_display = (
        "name",
        "workload",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
        "institution",
    )
    list_filter = [
        ("institution", custom_titled_filter("Institution")),
        ("formation", custom_titled_filter("Formation")),
        ("categories", custom_titled_filter("Category")),
        ("is_active", custom_titled_filter("Is Active")),
    ]
    search_fields = ["name"]
    list_select_related = ["institution"]
    autocomplete_fields = ["institution", "categories", "formation"]
    ordering = ["-end_date"]
    actions = [sync_selected_to_rag]


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    """Admin configuration for Certification model."""

    fields = [
        "name",
        "workload",
        "description",
        "credential_url",
        "credential_id",
        "issue_date",
        "expiration_date",
        "institution",
        "categories",
        "is_active",
    ]
    list_display = (
        "name",
        "institution",
        "issue_date",
        "expiration_date",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = [
        ("institution", custom_titled_filter("Institution")),
        ("categories", custom_titled_filter("Category")),
        ("is_active", custom_titled_filter("Is Active")),
    ]
    search_fields = ["name", "credential_id"]
    list_select_related = ["institution"]
    autocomplete_fields = ["institution", "categories"]
    ordering = ["-issue_date"]
    actions = [sync_selected_to_rag]
