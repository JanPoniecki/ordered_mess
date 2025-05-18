from django.contrib import admin
from .models import Room, Container, Item

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)
    list_filter = ('color',)

@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    list_filter = ('location',)
    search_fields = ('name', 'location__name')
    ordering = ('location', 'name')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'container', 'get_location')
    list_filter = ('container__location', 'container')
    search_fields = ('name', 'features', 'container__name', 'container__location__name')
    readonly_fields = ('features',)
    ordering = ('name',)

    def get_location(self, obj):
        return obj.container.location.name if obj.container else '-'
    get_location.short_description = 'Location'
