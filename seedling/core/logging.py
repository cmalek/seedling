from ..logging import get_logger, log_compat
from .modeldict import model_to_dict


def log_model_changes(original, new):
    """
    Logs the changes made from the original instance to new instance.
    """
    logger = get_logger()
    original_dict = model_to_dict(original, exclude_passwords=True)
    new_dict = model_to_dict(new, exclude_passwords=True)

    changes = {}
    for field_name, original_value in original_dict.items():
        new_value = new_dict.get(field_name)
        try:
            if original_value != new_value:
                changes[field_name] = '"{}" -> "{}"'.format(original_value, new_value)
        except TypeError:
            # Some fields (e.g. dates) can potentially trigger this kind of error when being compared. If that happens,
            # there's not much we can do about it, so we just skip that field.
            pass
    if changes:
        if original._meta.label == 'custom_auth.User':
            if 'last_login' in changes and len(changes) == 1:
                # Don't log changes that are only to the "last_login" field on the auth.User model.
                # That field gets changed every time the user logs in, and we already log logins.
                return
            if 'password' in changes:
                # Don't log the new password hash
                changes['password'] = "__NEW_PASSWORD__"
        # Don't let the "model" keyword that we set manually on info() conflict with the "changes" dict, which can
        # happen when renaming a model in a migration.
        if 'model' in changes:
            changes['other_model'] = changes.pop('model')
        logger.info('model.update', model=original._meta.label, pk=original.pk, **changes)


def log_model_m2m_changes(instance, action, model, pk_set):
    """
    Logs the changes made to an object's many-to-many fields.
    """
    logger = get_logger()

    # The post_add and post_remove signals get sent even if no changes are actually made by their respective actions
    # (e.g. when add()'ing an object that's already in the m2m relationship).
    # Since there are no changes, there's nothing to log.
    if not pk_set:
        return

    if action == "post_remove":
        removed_objects = model.objects.filter(pk__in=pk_set)
        logger.info(
            'model.m2m.delete',
            model=instance._meta.label,
            objects=", ".join(log_compat(obj) for obj in removed_objects),
            instance=log_compat(instance)
        )
    elif action == "post_add":
        added_objects = model.objects.filter(pk__in=pk_set)
        logger.info(
            'model.m2m.add',
            model=instance._meta.label,
            objects=", ".join(log_compat(obj) for obj in added_objects),
            instance=log_compat(instance)
        )


def log_new_model(instance):
    """
    Logs the field values set on a newly-saved model instance.
    """
    logger = get_logger()

    kwargs = model_to_dict(instance, exclude_passwords=True)
    if 'model' not in kwargs:
        kwargs['model'] = instance._meta.label
    if 'event' in kwargs:
        # the first argument to logger.info here is technically a kwarg called
        # 'event', so if kwargs also has a key in it called 'event', our
        # logger.info call will raise an exception about duplicate keyword args
        kwargs['event_obj'] = kwargs['event']
        del kwargs['event']
    logger.info('model.create', instance=log_compat(instance), **kwargs)


def log_model_deletion(instance):
    """
    Logs the deletion of this model instance.
    """
    logger = get_logger()

    kwargs = model_to_dict(instance, exclude_passwords=True)
    if 'event' in kwargs:
        # the first argument to logger.info here is technically a kwarg called
        # 'event', so if kwargs also has a key in it called 'event', our
        # logger.info call will raise an exception about duplicate keyword args
        kwargs['event_obj'] = kwargs['event']
        del kwargs['event']
    if 'model' in kwargs:
        # Some models have a "model" keyword, which needs to be removed for the same reason as 'event'.
        kwargs['model_obj'] = kwargs['model']
        del kwargs['model']
    logger.info('model.delete', model=instance._meta.label, instance=log_compat(instance), **kwargs)
