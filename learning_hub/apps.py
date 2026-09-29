from django.apps import AppConfig


class LearningHubConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "learning_hub"
    verbose_name = "Learning Hub"

    def ready(self):
        import learning_hub.signals  # noqa: F401
