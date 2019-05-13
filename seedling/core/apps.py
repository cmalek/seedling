from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Seedling Core'
    ready_is_done = False

    def ready(self):
        """
        This function runs as soon as the app is loaded. It loads our signal receivers.
        """
        # As suggested by the Django docs, we need to make absolutely certain that this code runs only once.
        if not self.ready_is_done:
            # See https://docs.djangoproject.com/en/1.9/topics/signals/#connecting-receiver-functions, in the
            # "Where should this code live?" section, for why this import is inside CoreConfig.ready().
            # noinspection PyUnresolvedReferences
            # from . import signals
            self.ready_is_done = True
        else:
            print("{}.ready() executed more than once! This method's code is skipped on subsequent runs.".format(
                self.__class__.__name__
            ))
