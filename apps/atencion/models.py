from django.db import models
from django.urls import reverse

from apps.afiliacion.mixins import CIEMixin, CitaMixin
from apps.afiliacion.models import Paciente, PacienteMixin, ATLugarAbordaje
from apps.common import constants
from apps.medicamentos.models import Medicamento


class ExamenFisico(models.Model):
    descripcion = models.CharField(max_length=100)
    estado = models.IntegerField(default=1)

    def __str__(self):
        return self.descripcion

    @classmethod
    def initial(cls):
        return [{'examen_fisico': e.pk} for e in cls.objects.filter(estado=1)]

    @classmethod
    def size(cls):
        try:
            tamanano = cls.objects.filter(estado=1).count()
        except Exception as e:
            return 0
        return tamanano


class Atencion(CitaMixin):
    paciente = models.ForeignKey(Paciente, verbose_name='Atención', to_field='paciente')
    medico = models.CharField(max_length=36)
    eess = models.CharField(max_length=36)
    ups = models.CharField('UPS', max_length=10, blank=True)
    nombre_ups = models.CharField('Nombre UPS', max_length=250, blank=True)
    fecha = models.DateField(auto_now=True)
    cita_uuid = models.UUIDField(verbose_name='Cita',  null=True)
    id_financiador = models.CharField(
        max_length=2,
        choices=constants.FINANCIADOR_CHOICES,
        default='0')
    contrato = models.CharField(max_length=50, null=True, blank=True)
    tipo_seguro = models.CharField(max_length=50, null=True, blank=True)
    tipo_seguro_descripcion = models.CharField(max_length=50, null=True, blank=True)
    regimen = models.CharField(max_length=50, null=True, blank=True)
    codigo_eess = models.CharField(max_length=8, null=True, blank=True)
    nombre_eess = models.CharField(max_length=250, null=True, blank=True)
    tipo_atencion = models.IntegerField(
        choices=constants.TIPO_ATENCION_CHOICES,
        default=constants.TIPO_ATENCION_DEMANDA)
    estado_cita = models.IntegerField(
        choices=constants.ESTADO_CITA_CHOICES,
        default=constants.ESTADO_CITA_PENDIENTE)
    estado_atencion = models.IntegerField(
        choices=constants.ESTADO_ATENCION_CHOICES,
        default=constants.ESTADO_ATENCION_PENDIENTE
    )
    tipo_registro = models.CharField(max_length=5, choices=constants.PACIENTE_VIH, blank=True, null=True)
    lugar_abordaje = models.ForeignKey(ATLugarAbordaje, verbose_name='Atención lugar de Abordaje', null=True)

    class Meta:
        verbose_name_plural = 'Atenciones'
        ordering = ('-fecha',)
        unique_together = ('eess', 'medico', 'paciente', 'cita_uuid', 'ups', 'fecha')

    @property
    def get_atencion_antecedentes_url(self):
        return reverse('atencion:atencion_antecedente', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_triaje_url(self):
        return reverse('atencion:atencion-inicial-new', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_definicion_url(self):
        return reverse('atencion:atencion-dx-definicion', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_tarv_url(self):
        return reverse('atencion:atencion-tratamiento', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_g_url(self):
        return reverse('atencion:atencion-gestacion', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_terapia_url(self):
        return reverse('atencion:atencion-terapia', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_ram_url(self):
        return reverse('atencion:atencion-ram', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_ex_aux_url(self):
        return reverse('atencion:atencion-examenauxiliar', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_coinfeccion_url(self):
        return reverse('atencion:atencion-descarte', kwargs=dict(pk=self.pk, uuid=self.paciente.pk))

    @property
    def get_atencion_cronograma_url(self):
        return reverse('atencion:atencion-cronograma-control', kwargs=dict(pk=self.pk))

    def get_absolute_url(self):
        return reverse('atencion:atencion_cita', kwargs=dict(pk=self.pk))


class Triaje(models.Model):
    atencion = models.OneToOneField(Atencion, verbose_name='Atención')
    anamnesis = models.CharField(verbose_name='Anamnesis', max_length=500, null=True)
    peso = models.DecimalField(verbose_name='Peso', max_digits=6, decimal_places=2, null=True)
    talla = models.DecimalField(verbose_name='Talla', max_digits=6, decimal_places=2, null=True)
    temperatura = models.DecimalField(verbose_name='Temp', max_digits=6, decimal_places=2, null=True)
    imc = models.DecimalField(verbose_name='IMC', max_digits=6, decimal_places=2, null=True)
    frecuencia_cardiaca = models.DecimalField(verbose_name='FC', max_digits=6, decimal_places=2, null=True)
    frecuencia_respiratoria = models.DecimalField(verbose_name='FR', max_digits=6, decimal_places=2, null=True)

    def __str__(self):
        return 'Atencion'

    def get_absolute_url(self):
        return reverse('atencion:atencion-inicial-edit',
                       kwargs=dict(pk=self.atencion.pk, uuid=self.atencion.paciente, id=self.pk))


class AtencionExamenFisico(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    examen_fisico = models.ForeignKey(ExamenFisico, verbose_name='Exámen Físico')
    estado = models.CharField(max_length=2, verbose_name='Estado', default='1', blank=True)
    obs = models.CharField(max_length=500, verbose_name='Observación', blank=True)


class AtencionDiagnostico(CIEMixin):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    estadio = models.CharField(max_length=2, verbose_name='Estadío', choices=constants.ESTADIO_INFEC_CHOICES,
                               default='1')
    tipo_dx = models.CharField(max_length=2, verbose_name='Tipo de Dx')
    indicacion = models.CharField(max_length=500, verbose_name='Indicación', null=True)


class AtencionTratamiento(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    medicamento = models.ForeignKey(Medicamento, related_name="medicamento_trat")
    cantidad_dia = models.PositiveSmallIntegerField(default=1, verbose_name='N° a suministrar por dia')
    nro_dias = models.PositiveSmallIntegerField(default=1, verbose_name='N° de dias')
    indicacion = models.CharField(max_length=500, verbose_name='Indicación', blank=True)
    estado = models.CharField(
        verbose_name='Estado del tratamiento',
        max_length=150,
        choices=constants.ATENCION_TRATAMIENTO_ESTADO,
        default=constants.EN_CURSO)

    class Meta:
        unique_together = ('atencion', 'medicamento')

    def _get_total(self):
        return self.nro_dias * self.cantidad_dia

    total = property(_get_total)


class AtencionGestacion(models.Model):
    atencion = models.OneToOneField(Atencion, verbose_name='Atención', related_name='gestacion_atencion')
    fur = models.DateField('FUR', null=True, blank=True)
    fpp = models.DateField('FPP', null=True, blank=True)
    edad = models.PositiveSmallIntegerField('Edad Gestacional', default=1)


class AtencionTerapia(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    tuvo_terapia = models.BooleanField(default=True)
    terapia = models.IntegerField(default=constants.RIFAPENTINA_ISONIACIDA, choices=constants.TERAPIA_PREVENTIVA)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    razon = models.TextField(blank=True)


class AtencionRam(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    ram = models.ForeignKey(Medicamento, verbose_name='Medicamento')
    descripcion = models.CharField(max_length=500, verbose_name='Descripción de la RAM', null=True)
    fg_presenta_ram = models.BooleanField(default=False)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    fg_gravedad = models.IntegerField('Gravedad', choices=constants.ESTADO_GRAVEDAD_CHOICES, default=1)
    descripcion_gravedad = models.CharField(max_length=500, verbose_name='Cuando RAM es grave', blank=True)


class AtencionExamenAuxiliar(models.Model):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    imagen = models.CharField(max_length=10, blank=True)
    imagen_fecha = models.DateField(null=True, blank=True)
    laboratorio = models.CharField(max_length=10, blank=True)
    laboratorio_fecha = models.DateField(null=True, blank=True)
    procedimiento = models.CharField(max_length=10, blank=True)
    procedimiento_fecha = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Exámenes Auxiliar'


class AtencionDescarteCoinfeccion(CIEMixin):
    atencion = models.ForeignKey(Atencion, verbose_name='Atención')
    observacion = models.CharField(max_length=500, verbose_name='Observación', blank=True)
    fecha_descarte = models.DateField(null=True, blank=True)
    infeccion = models.IntegerField()


class AtencionFrecuencia(models.Model):
    descripcion = models.CharField(max_length=10, verbose_name="Descripción")
    tiempo_dias = models.IntegerField()

    def __str__(self):
        return self.descripcion

    class Meta:
        ordering = ('pk', )


class AtencionControl(models.Model):
    descripcion = models.CharField(max_length=50, verbose_name="Descripción")
    codigo = models.IntegerField()
    tipo = models.IntegerField(choices=constants.ATENCION_CONTROL_CHOICES)
    estado = models.IntegerField(default=1)

    def __str__(self):
        return self.descripcion

    class Meta:
        ordering = ('pk', )


class AtencionControlXFrecuencia(models.Model):
    control = models.ForeignKey(AtencionControl)
    frecuencia = models.ForeignKey(AtencionFrecuencia)

    def __str__(self):
        return self.control.descripcion + ' - ' + self.frecuencia.descripcion

    class Meta:
        verbose_name = 'Relación Control por Frecuencia'
        verbose_name_plural = 'Relación Control por Frecuencia'


class AtencionFrecuenciaControl(PacienteMixin):
    atencion = models.ForeignKey(Atencion, verbose_name="Atención")
    estado = models.IntegerField(default=1)

    def _get_detalle(self):
        return AtencionFrecuenciaControlDetalle.objects.filter(atencion_frecuencia_control=self)

    detalle_frecuencia = property(_get_detalle)


class AtencionFrecuenciaControlDetalle(models.Model):
    atencion_frecuencia_control = models.ForeignKey(AtencionFrecuenciaControl)
    control = models.ForeignKey(AtencionControl)
    frecuencia = models.ForeignKey(AtencionFrecuencia)
    fecha_programada = models.DateField()
    nueva_fecha_programada = models.DateField(null=True)
    fecha_atencion = models.DateField(null=True)
    check = models.IntegerField(default=0)  # Indica si en esa fecha con el control toca atención


class Egreso(models.Model):
    atencion = models.ForeignKey(Atencion, related_name="egresos")
    tipo_egreso = models.IntegerField(choices=constants.TIPO_EGRESO_CHOICES)
    numero_episodio = models.IntegerField(choices=constants.EGRESO_EPISODIO_CHOICES, null=True, blank=True)
    lugar_fallecimiento = models.IntegerField(
        choices=constants.EGRESO_LUGAR_FALLECIMIENTO_CHOICES,
        null=True,
        blank=True
    )
    fecha_egreso = models.DateField()
    causa_fallecimiento = models.TextField('Causa de Fallecimiento', blank=True)
    creator = models.CharField(max_length=20)
    modifier = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = 'Egreso'
        verbose_name_plural = 'Egresos'
        ordering = ('pk',)
