from django.contrib import admin

from .models import Poblacion, Brigada, ATLugarAbordaje


@admin.register(Poblacion)
class PoblacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'denominacion')


@admin.register(Brigada)
class BrigadaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'ubigeo_departamento', 'ubigeo_provincia',
        'ubigeo_distrito', 'nombre_departamento',
        'nombre_provincia', 'nombre_distrito'
    )
    search_fields = (
        'nombre', 'nombre_departamento', 'nombre_provincia',
        'nombre_distrito'
    )
    list_filter = (
        'nombre_departamento', 'nombre_provincia', 'nombre_distrito'
    )


@admin.register(ATLugarAbordaje)
class ATLugarAbordajeAdmin(admin.ModelAdmin):
    list_display = (
        'brigada', 'lugar_abordaje', 'detalle',
        'fecha_abordaje', 'distrito_lugar_abordaje',
        'nombre_lugar', 'latitud', 'longitud'
    )
    search_fields = (
        'lugar_abordaje', 'detalle', 'distrito_lugar_abordaje',
        'nombre_lugar'
    )
    list_filter = ('lugar_abordaje', 'distrito_lugar_abordaje')
