from django.apps import AppConfig


class DjangoMtgResConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_mtg_res"
    label = "res"  # Keep the original label to avoid migration issues
