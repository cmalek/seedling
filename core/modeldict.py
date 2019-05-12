from itertools import chain

from django.db.models.fields.related import ManyToManyField
from django.db.models.query import QuerySet


# CPM: I moved these two model_to_dict* functions here from core.utils because
# some logging functions need it, but some functions in core.utils need those
# logging functions and that caused a circular import

def model_to_dict(instance, exclude_passwords=False):
    """
    Convert the given model instance to a dictionary keyed by field name.
    Pass in exclude_passwords = True to skip any field named "password". This is primarily useful to prevent
    hashed passwords from being logged when a User object is created or changed.
    """
    data = {}
    for f in instance._meta.get_fields():
        if not isinstance(f, ManyToManyField) and (exclude_passwords and f.name != 'password'):
            if hasattr(f, 'value_from_object'):
                try:
                    data[f.name] = f.value_from_object(instance)
                except:
                    # If anything goes wrong at this step, just ignore this field.
                    pass
                else:
                    if isinstance(data[f.name], QuerySet):
                        # Convert QuerySets to concrete lists, so they're printable and comparable (for logging).
                        data[f.name] = list(data[f.name].all())
            else:
                field_data = getattr(instance, f.name, None)
                try:
                    # If this field is a manager, grab all the managed objects.
                    field_data = list(field_data.all())
                except AttributeError:
                    pass
                data[f.name] = field_data
    return data


def model_to_dict_deep_copy(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.many_to_many):
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance))
        else:
            data[f.name] = f.value_from_object(instance)
    return data


