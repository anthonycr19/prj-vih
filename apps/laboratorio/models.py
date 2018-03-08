from django.db import models

from apps.common import constants
from apps.afiliacion.mixins import PacienteMixin, CPTMixin
from apps.consejeria.models import Consejeria


class Examen(PacienteMixin, CPTMixin):
    consejeria_pre = models.ForeignKey(Consejeria, null=True, blank=True, on_delete=models.CASCADE)
    personal_salud = models.CharField(max_length=100, verbose_name='Personal de Salud', null=True)
    eess = models.CharField(max_length=15, verbose_name='Establecimiento')
    estado = models.CharField(max_length=1, choices=constants.ESTADO_EXAMEN_CHOICES, default='1')
    observaciones = models.CharField(max_length=500, blank=True)
    fecha_prueba = models.DateField(null=True, blank=True)
    codigo_muestra = models.CharField(max_length=50, null=True, blank=True)
    codigo_qr = models.CharField(max_length=100, blank=True)
    hora_solicitud = models.TimeField(null=True, blank=True)
    nombre = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ('-fecha_prueba', )


class ExamenResultado(models.Model):
    laboratorio_examen = models.ForeignKey(Examen, related_name='resultados', verbose_name='Exámen')
    resultado = models.CharField(max_length=30, choices=constants.RESULTADO_EXAMEN)
    nro_prueba = models.PositiveSmallIntegerField('Número de prueba', null=True, blank=True)
    nro_muestra = models.CharField('Número de muestra', max_length=30, blank=True)
    fecha_resultado = models.DateField('Fecha de resultado', null=True, blank=True)
    observacion = models.TextField('Observación', blank=True)
    post_test = models.BooleanField(default=False)
    ficha_informativa = models.BooleanField(default=False)
    refiere_eess = models.BooleanField(default=False)
    codigo_eess = models.CharField(max_length=36, null=True, blank=True)
    nombre_eess = models.CharField(max_length=150, null=True, blank=True)
    fecha_cita = models.DateField(null=True)
    fecha_registro = models.DateField(null=True)
    repite_prueba = models.BooleanField(default=False)
    cantidad_condones = models.IntegerField(default=0)
    cantidad_lubricantes = models.IntegerField(default=0)
