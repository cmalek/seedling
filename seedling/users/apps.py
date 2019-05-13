from django.apps import AppConfig


class UsersAppConfig(AppConfig):

    name = "seedling.users"
    verbose_name = "Users"

    def ready(self):
        try:
            import seedling.users.signals  # noqa F401
        except ImportError:
            pass
