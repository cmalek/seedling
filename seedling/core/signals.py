"""
Because the act of importing this file registers the signal handlers, it must only be imported from within
core.apps.CoreConfig.ready(). See https://docs.djangoproject.com/en/1.9/topics/signals/#connecting-receiver-functions
"""
from django.conf import settings
from django.db.models.signals import pre_save, post_save, m2m_changed, pre_delete
from django.dispatch.dispatcher import receiver
from djunk.logging import log_model_changes, log_new_model, log_model_m2m_changes, log_model_deletion

from ..logging import logger

# NOTE: Signals are not loaded by default. Uncomment the signals import line in core.apps.CoreConfig to enable them.

# noinspection PyUnusedLocal
@receiver(pre_save)
def log_model_instance_changes(sender, instance, raw, using, update_fields, **kwargs):
    """
    Log the changes made to all model instances, except for models that we've been told to skip.
    Also skip if raw = True, aka when loading fixtures.
    """
    if not raw and instance._meta.label not in settings.UNLOGGED_MODELS:
        try:
            original_instance = sender.objects.get(pk=instance.pk)
            log_model_changes(logger, original_instance, instance)
        except sender.DoesNotExist:
            # This will happen the first time the object is saved, since an original_instance doesn't exist.
            pass


# noinspection PyUnusedLocal
@receiver(post_save)
def log_model_instance_creations(sender, instance, raw, created, using, update_fields, **kwargs):
    """
    Log the creation of all model instances, except for models that we've been told to skip.
    Also skip if raw = True, aka when loading fixtures.
    """
    if not raw and created and instance._meta.label not in settings.UNLOGGED_MODELS:
        log_new_model(logger, instance)


# noinspection PyUnusedLocal
@receiver(m2m_changed)
def log_model_instance_m2m_changes(sender, action, instance, reverse, model, pk_set, using, **kwargs):
    if instance._meta.label not in settings.UNLOGGED_MODELS:
        log_model_m2m_changes(logger, instance, action, model, pk_set)


# noinspection PyUnusedLocal
@receiver(pre_delete)
def log_model_deletions(sender, instance, using, **kwargs):
    """
    Log the deletions of all model instances, except for models that we've been told to skip.
    """
    if instance._meta.label not in settings.UNLOGGED_MODELS:
        log_model_deletion(logger, instance)
