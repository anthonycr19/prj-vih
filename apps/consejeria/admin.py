from django.contrib import admin
from apps.consejeria.models import Consejeria, ConsejeriaPre, ConsejeriaPost


@admin.register(Consejeria)
class ConsejeriaAdmin(admin.ModelAdmin):
    list_display = ('atencion', 'tipo_consejeria')
    list_filter = ('tipo_consejeria', )


@admin.register(ConsejeriaPre)
class ConsejeriaPreAdmin(admin.ModelAdmin):
    list_display = ('consejeria', 'tipo_poblacion', 'consejeria_previa', 'esta_consentido')
    list_filter = ('tipo_poblacion', 'consejeria_previa', 'esta_consentido')


@admin.register(ConsejeriaPost)
class ConsejeriaPostAdmin(admin.ModelAdmin):
    pass
