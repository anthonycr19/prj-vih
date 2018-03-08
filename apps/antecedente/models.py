from django.db import models

from apps.afiliacion.mixins import CIEMixin
from apps.atencion.models import Atencion
from apps.medicamentos.models import Medicamento


class Parentesco(models.Model):
    descripcion = models.CharField(max_length=20)

    def __str__(self):
        return self.descripcion


class TipoEnfermedad(models.Model):
    descripcion = models.CharField(max_length=70)

    def __str__(self):
        return self.descripcion


class Terapia(models.Model):
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion


class Vacunas(models.Model):
    codigo = models.CharField(max_length=100, null=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion


class AntecedentePersonal(CIEMixin):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención', related_name='antecedente_personal_atencion')
    tipo_enfermedad = models.ForeignKey(TipoEnfermedad, verbose_name='Tipo de Enfermedad')
    fecha_dx = models.DateField()
    obs = models.TextField(blank=True)
    fecha_registro = models.DateField(auto_now=True)

    def __str__(self):
        return self.cie


class AntecedenteFamiliar(CIEMixin):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención', related_name='antecedente_familiar_atencion')
    parentesco = models.ForeignKey(Parentesco, null=True)
    obs = models.TextField(blank=True)
    fecha_dx = models.DateField()
    fecha_registro = models.DateField(auto_now=True)

    def __str__(self):
        return self.cie


class AntecedenteTerapiaAntirretroviral(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención', related_name='antecedente_familiar_antirretroviral')
    medicamento1 = models.ForeignKey(Medicamento, related_name="medicamento1")
    medicamento2 = models.ForeignKey(Medicamento, related_name="medicamento2")
    medicamento3 = models.ForeignKey(Medicamento, related_name="medicamento3", null=True, blank=True)
    medicamento4 = models.ForeignKey(Medicamento, related_name="medicamento4", null=True, blank=True)
    medicamento5 = models.ForeignKey(Medicamento, related_name="medicamento5", null=True, blank=True)
    fecha_inicio = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)
    obs = models.CharField(max_length=500, null=True)
    fecha_registro = models.DateField(auto_now=True)
    esquema = models.IntegerField(null=True)
    descripcion = models.CharField(max_length=250, null=True)

    class Meta:
        ordering = ('-fecha_inicio', )

    def __str__(self):
        return str(self.descripcion)


class AntecedenteTerapiaPreventiva(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención', related_name='antecedente_familiar_preventiva')
    tiene_terapia_tub = models.BooleanField(default=False)
    razon_cambio_tub = models.CharField(max_length=500, blank=True)
    fecha_inicio_tub = models.DateField(null=True)
    tiene_terapia_pne = models.BooleanField(default=False)
    razon_cambio_pne = models.CharField(max_length=500, blank=True)
    fecha_inicio_pne = models.DateField(null=True)

    def __str__(self):
        return ''


class AntecedenteVacunaRecibida(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención', related_name='antecedente_familiar_vacuna')
    vacuna = models.ForeignKey(Vacunas, verbose_name='Vacuna')
    nro_dosis = models.PositiveSmallIntegerField('Dosis', default=1)
    fecha_aplicacion = models.DateField('Fecha aplicación', null=True)

    def __str__(self):
        return str(self.vacuna)
