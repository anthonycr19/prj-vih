from django.contrib import admin

from .models import Medicamento, Esquema


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'descripcion', 'presentacion', 'concentracion', 'abreviatura', 'targa')
    list_editable = ('abreviatura', 'codigo', 'descripcion', 'presentacion', 'concentracion', 'targa')
    search_fields = ('codigo', 'descripcion', 'abreviatura')


@admin.register(Esquema)
class EsquemaAdmin(admin.ModelAdmin):
    filter_horizontal = ['medicamentos', ]
