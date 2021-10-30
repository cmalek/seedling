from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    full_name = CharField(_("Full Name"), blank=True, max_length=255)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
