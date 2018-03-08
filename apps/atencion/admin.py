from django.contrib import admin

from .models import (Atencion, AtencionTratamiento, AtencionDiagnostico, AtencionControlXFrecuencia, ExamenFisico,
                     AtencionFrecuencia, AtencionControl)


@admin.register(AtencionControlXFrecuencia)
class AtencionControlXFrecuenciaAdmin(admin.ModelAdmin):
    list_display = ('control', 'frecuencia')
    list_filter = ('control', )


admin.site.register(ExamenFisico)
admin.site.register(Atencion)
admin.site.register(AtencionTratamiento)
admin.site.register(AtencionDiagnostico)
admin.site.register(AtencionFrecuencia)
admin.site.register(AtencionControl)
