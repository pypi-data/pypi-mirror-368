from django.contrib import admin

from .models import PLZdb


@admin.register(PLZdb)
class PLZdbAdmin(admin.ModelAdmin):
    list_display = ["name", "plz", "coordinates"]
    search_fields = ["name", "plz"]
    ordering = ["name"]

    def coordinates(self, obj):
        if obj.coord_x:
            return f"{obj.coord_x}/{obj.coord_y}"
        else:
            return ""
    
