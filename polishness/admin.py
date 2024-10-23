from __future__ import annotations

from django.contrib import admin

from .models import ArcheologicalMonument
from .models import Monument


class MonumentAdmin(admin.ModelAdmin):
    list_display = ("name", "function", "chronology", "voivodeship", "county", "parish", "locality")


class ArcheologicalMonumentAdmin(admin.ModelAdmin):
    list_display = ("name", "function", "chronology", "voivodeship", "county", "parish", "locality")


admin.site.register(Monument, MonumentAdmin)
admin.site.register(ArcheologicalMonument, ArcheologicalMonumentAdmin)
