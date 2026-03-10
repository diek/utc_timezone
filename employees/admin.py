# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Geography, Position, Employee


@admin.register(Geography)
class GeographyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'timezone')
    search_fields = ('name',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'geography',
        'surname',
        'given_name',
        'position',
        'email',
        'user',
    )
    list_filter = ('geography', 'position', 'user')
