#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.migrations.loader import MigrationLoader
from django.core.management import call_command
from django.core.management.base import BaseCommand

from seedling.logging import logger  # noqa:E402


class Command(BaseCommand):
    """
    Do our initial migrate and data load if necessary.

    If `settings.BOOTSTRAP_ALWAYS_MIGRATE` is `True`, always run migrations.
    """
    def db_is_fresh(self, database):
        """
        Figure out if we've never run migrations here.

        Assume that if the contenttypes.0001_initial migration has not run,
        we have a fresh database.
        """
        connection = connections[database]
        loader = MigrationLoader(connection)
        return ('contenttypes', '0001_initial') not in loader.applied_migrations

    def handle(self, **options):
        logger.info('migrate.start')
        if self.db_is_fresh(DEFAULT_DB_ALIAS):
            call_command("migrate")
            if settings.DEVELOPMENT:
                call_command("loaddata", "sites")
                call_command("loaddata", "dev-users")
        elif settings.BOOTSTRAP_ALWAYS_MIGRATE:
            call_command("migrate")
        logger.info('migrate.end')
