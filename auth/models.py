from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Replaces the auth.User model with our customized version.
    """
    pass
