from django.db import models

from apps.afiliacion.models import Poblacion
from apps.atencion.models import Atencion
from apps.common import constants
from apps.common.constants import Antecendentes, Transmision


class Consejeria(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    tipo_consejeria = models.IntegerField(choices=constants.TIPO_CONSEJERIA, default=constants.PRE)
    fecha_registro = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('fecha_registro', )

    def __str__(self):
        return 'Conserjeria N° {}'.format(self.id)


class ConsejeriaPre(models.Model):
    consejeria = models.OneToOneField(Consejeria, verbose_name='Consejeria')
    tipo_poblacion = models.ForeignKey(Poblacion, verbose_name='Tipo de Poblacion')
    consejeria_previa = models.BooleanField(default=False, verbose_name='¿Recibio Consejeria Previa?')
    esta_consentido = models.BooleanField(default=False, verbose_name='Firmar Consentimiento Informado')
    validacion = models.TextField(blank=True)

    class Meta:
        ordering = ('consejeria__fecha_registro', )

    def __str__(self):
        return 'Pre Conserjeria N° {}'.format(self.id)


class ConsejeriaPost(models.Model):
    consejeria = models.OneToOneField(Consejeria, verbose_name='Consejeria')
    via_transmision = models.CharField(max_length=250, blank=True)
    antecedentes = models.CharField(max_length=250, blank=True, choices=Antecendentes.to_choice())
    tipo_transmision = models.CharField(max_length=250, blank=True, choices=Transmision.to_choice())
    nro_parejas = models.IntegerField(default=1, null=True)
    uso_preservativo = models.BooleanField(default=False)

    def __str__(self):
        return 'Post Conserjeria N° {}'.format(self.id)
