from __future__ import annotations

from django.contrib import admin

from .models import Monument


class MonumentAdmin(admin.ModelAdmin):
    list_display = ("name", "function", "voivodeship", "county", "parish", "locality")


admin.site.register(Monument, MonumentAdmin)
