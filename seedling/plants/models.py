from django.db import models
from multitenancy.models import SiteSpecificModel
from django_extensions.db.fields import AutoSlugField
import reversion

from ..core.models import AuditableMixin


class PlantType(AuditableMixin, SiteSpecificModel):
    """
    This is a lookup table for plant type.
    """

    name = models.CharField(max_length=32)
    slug = AutoSlugField(populate_from=['name'])
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "plant_type"
        verbose_name = "Plant Type"
        verbose_name_plural = "Plant Types"
        ordering = ["name"]
        unique_together = ['site', 'name']


class PlantSource(AuditableMixin, SiteSpecificModel):

    name = models.CharField(max_length=255)
    url = models.URLField('Source Website', blank=True, null=True)
    slug = AutoSlugField(populate_from=['name'])

    class Meta:
        db_table = "plant_type"
        verbose_name = "Plant Type"
        verbose_name_plural = "Plant Types"
        ordering = ["name"]
        unique_together = ['site', 'name']


class GrowingSeason(AuditableMixin, SiteSpecificModel):

    name = models.CharField(max_length=32)
    slug = AutoSlugField(populate_from=['name'])
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "season"
        verbose_name = "Growing Season"
        verbose_name_plural = "Growing Seasons"
        ordering = ["name"]
        unique_together = ['site', 'name']


class SunExposure(AuditableMixin, SiteSpecificModel):

    name = models.CharField(max_length=32)
    slug = AutoSlugField(populate_from=['name'])
    details = models.CharField(max_length=255)

    class Meta:
        db_table = "sun_exposure"
        verbose_name = "Sun Exposure"
        verbose_name_plural = "Sun Exposures"
        ordering = ["name"]
        unique_together = ['site', 'name']


@reversion.register()
class Plant(SiteSpecificModel):

    name = models.CharField(
        verbose_name='Common Name',
        max_length=128,
        help_text="Common name for this plant"
    )
    sku = models.CharField(
        verbose_name='Inventory SKU',
        max_length=32,
    )

    latin_name = models.CharField(
        verbose_name='Latin Name',
        max_length=128,
        blank=True,
        null=True,
        help_text="Latin name for this plant, e.g. <em>Lathyrus odoratus</em>"

    )
    plant_family = models.ForiegnKey(
        PlantType,
        verbose_name="Plant Family",
        on_delete=models.PROTECT,
        help_text="Of which plant family is this plant a part?"
    )
    season = models.ManyToManyField(
        GrowingSeason,
        on_delete=models.PROTECT,
        null=True,
        db_table='plant_season',
        help_text="During what growing seasons does this plant grow?"
    )

    # plant image
    # seed image
    # seed flowering image

    # Consider django-measurement for this
    plant_height = models.IntegerField(
        'Plant height',
        blank=True,
        null=True,
        help_text="Average height of plant when full grown, in inches"
    )

    # ------------------
    # Planting info
    # ------------------

    planting_instructions = models.TextField(
        verbose_name='Planting Instructions',
        blank=True,
        null=True,
        help_text="Enter any planting instructions specific to this plant"
    )
    # Consider django-measurement for this
    planting_depth = models.IntegerField(
        verbose_name='Planting depth',
        blank=True,
        null=True,
        help_text="Optimal planting depth for seeds, in inches"
    )
    # Consider django-measurement for this
    planting_spacing = models.IntegerField(
        'Planting spacing',
        blank=True,
        null=True,
        help_text="Optimal spacing for plants when planting, in inches"
    )

    # ------------------
    # Growing info
    # ------------------

    growing_instructions = models.TextField(
        verbose_name='Growing Instructions',
        blank=True,
        null=True,
        help_text="Enter any post-planting growing instructions here."
    )

    sun = models.ForeignKey(
        verbose_name='Sun Exposure',
        on_delete=models.PROTECT,
        null=True,
        help_text='What kind of sun does this plant need?'
    )

    water = models.TextField(
        verbose_name='Watering requirements',
        blank=True,
        null=True,
        help_text='Watering instructions for this plant?'
    )

    days_to_germination = models.PositiveIntegerField(
        verbose_name='Days to Germination',
        blank=True,
        null=True,
        help_text="Number of days since planting before the seed germinates"
    )

    days_to_germination = models.PositiveIntegerField(
        verbose_name='Days to Maturity',
        blank=True,
        null=True,
        help_text="Number of days since planting before the plant is mature"
    )

    days_to_seed_output = models.PositiveIntegerField(
        verbose_name='Days to Maturity',
        blank=True,
        null=True,
        help_text="Number of days since planting before seeds can be "
                  "harvested from the mature plant"
    )

    seed_saving_instructions = models.TextField(
        verbose_name='Seed Saving Instructions',
        blank=True,
        null=True,
        help_text="Instructions on how to save seeds for this plant"
    )

    class Meta:
        db_table = "plant"
        verbose_name = "Plant"
        verbose_name_plural = "Plants"
        ordering = ["name"]
        unique_together = ['site', 'name']
