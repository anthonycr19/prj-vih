from django.db import models

from .querysets import MedicamentoQuerySet


class Medicamento(models.Model):
    codigo = models.IntegerField('Codigo', null=True)
    descripcion = models.CharField('Descripción', max_length=150)
    presentacion = models.CharField('Presentación', max_length=100)
    concentracion = models.CharField('Concentracion', max_length=100)
    abreviatura = models.CharField('Abreviatura', max_length=20, blank=True, null=True)
    targa = models.BooleanField('Usado en tratamiento Targa', default=False)

    objects = MedicamentoQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Medicamentos'
        ordering = ['descripcion', ]

    def __str__(self):
        return '{} {}'.format(self.descripcion or '', self.concentracion or '')

    @property
    def nombre_display(self):
        return '{} {}'.format(self.descripcion or '', self.concentracion or '')


class Esquema(models.Model):
    TIPO_CHOICES = (
        ('primera_linea', 'Primera Línea'),
        ('de_rescate', 'De Rescate'),
        ('otros', 'Otros'),
    )
    descripcion = models.CharField('Descripción', max_length=150)
    tipo = models.CharField('Tipo', choices=TIPO_CHOICES, max_length=20)
    etapa_crecimiento = models.IntegerField(choices=((0, 'Niño'), (1, 'Adulto')), null=True, blank=True)
    n_meses = models.IntegerField('Cantidad de Meses', null=True, blank=True)
    medicamentos = models.ManyToManyField(Medicamento, blank=True)

    class Meta:
        ordering = ('descripcion', )

    def __str__(self):
        return '({}) {}'.format(self.tipo, self.descripcion)

    @property
    def get_medicamentos(self):
        return ','.join(str(medicamentos.codigo) for medicamentos in self.medicamentos.all())

    @property
    def nombre_display(self):
        return '({}) {}'.format(self.tipo, self.descripcion)


class EsquemaMedicamento(models.Model):
    esquema = models.ForeignKey(Esquema)
    medicamento = models.ForeignKey(Medicamento)

    class Meta:
        managed = False
        db_table = 'medicamentos_esquema_medicamentos'
