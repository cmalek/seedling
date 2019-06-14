from django.contrib import admin

from multitenancy.admin import SiteSpecificModelAdmin

from .models import (
    GrowingSeason,
    Plant,
    PlantSource,
    PlantType,
    SunExposure
)


class GrowingSeasonAdmin(SiteSpecificModelAdmin):
    pass


class PlantSourceAdmin(SiteSpecificModelAdmin):
    pass


class PlantTypeAdmin(SiteSpecificModelAdmin):
    pass


class SunExposureAdmin(SiteSpecificModelAdmin):
    pass


class PlantAdmin(SiteSpecificModelAdmin):
    pass


admin.site.register(SunExposure, SunExposureAdmin)
admin.site.register(GrowingSeason, GrowingSeasonAdmin)
admin.site.register(PlantSource, PlantSourceAdmin)
admin.site.register(PlantType, PlantTypeAdmin)
admin.site.register(Plant, PlantAdmin)
