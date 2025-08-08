from django.contrib import admin
from .models import RequestLog
from django.utils.html import format_html
from .utils import try_get_pretty_json


# Register your models here.
@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "url",
        "method",
        "status_code",
        "ref_obj",
        "ref_id",
        "remarks",
        "created",
    )

    list_filter = ("method", "status_code", "ref_obj", "ref_id", "created")
    search_fields = ("url", "method", "status_code", "ref_obj", "ref_id", "remarks")
    readonly_fields = ("id", "created", "formatted_request", "formatted_response")
    ordering = ("-created",)

    fieldsets = (
        (None, {"fields": ("id", "created")}),
        ("Ref", {"fields": ("ref_obj", "ref_id", "remarks")}),
        (
            "Request",
            {
                "fields": (
                    "url",
                    "method",
                    "formatted_request",
                )
            },
        ),
        (
            "Response",
            {
                "fields": (
                    "status_code",
                    "formatted_response",
                )
            },
        ),
    )

    list_per_page = 10
    list_max_show_all = 100

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    @admin.display(description="Request")
    def formatted_request(self, instance):
        pretty_request = try_get_pretty_json(instance.request)
        return format_html(
            "<pre>{}</pre>",
            pretty_request,
        )

    @admin.display(description="Response")
    def formatted_response(self, instance):
        pretty_response = try_get_pretty_json(instance.response)
        return format_html("<pre>{}</pre>", pretty_response)
