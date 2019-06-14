from django.conf import settings
from django.db import models

from multitenancy.utils import get_current_user


class AuditableMixin(models.Model):
    """
    Add created_by and modified_by user fields to your model.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)_created_by'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)_updated_by'
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        """
        Update updated_by and created_by (if we're creating the model)
        with the currentl logged in user.
        """
        # TODO: this will be None if we're using a manage.py command
        #       need to do something reasonable
        user = get_current_user()
        if self.pk is None:
            # We're creating the model
            self.created_by = user
        self.updated_by = user
        super().save(*args, **kwargs)
