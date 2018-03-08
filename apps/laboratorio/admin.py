from django.contrib import admin

from .models import Examen, ExamenResultado


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'consejeria_pre', 'eess', 'estado', 'fecha_prueba')


@admin.register(ExamenResultado)
class ExamenResultadoAdmin(admin.ModelAdmin):
    pass
