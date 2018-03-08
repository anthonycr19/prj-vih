from django.contrib import admin

from .models import TipoEnfermedad, Parentesco, Vacunas


@admin.register(TipoEnfermedad)
class TipoEnfermedadAdmin(admin.ModelAdmin):
    pass


@admin.register(Parentesco)
class ParentescoAdmin(admin.ModelAdmin):
    pass


@admin.register(Vacunas)
class VacunasAdmin(admin.ModelAdmin):
    pass
