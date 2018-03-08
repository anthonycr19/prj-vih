import uuid
from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.utils import timezone
from mpi_client.client import CiudadanoClient

from apps.common import constants
from .mixins import PacienteMixin


class Paciente(PacienteMixin):
    paciente = models.UUIDField(verbose_name='Paciente', primary_key=True)
    nombres = models.CharField('Nombres', max_length=100, blank=True, null=True)
    apellido_paterno = models.CharField('Apellido Paterno', max_length=50, blank=True, null=True)
    apellido_materno = models.CharField('Apellido Materno', max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', blank=True, null=True)
    tipo_documento = models.CharField(
        'Tipo de Documento',
        choices=constants.TDOC_CHOICES,
        max_length=2,
        blank=True,
        null=True
    )
    numero_documento = models.CharField('Nº de Documento', max_length=12, blank=True, null=True)
    sexo = models.CharField('Sexo', choices=constants.SEXO_CHOICES, max_length=2, blank=True, null=True)
    estado_civil = models.CharField('Estado Civil', choices=constants.EC_CHOICES, max_length=2, blank=True, null=True)
    grado_instruccion = models.CharField(
        'Grado de instrucción',
        choices=constants.GI_CHOICES,
        max_length=2,
        null=True,
        blank=True
    )
    ocupacion = models.CharField(
        'Ocupacion',
        choices=constants.OCUPACION_CHOICES,
        max_length=2,
        null=True,
        blank=True
    )
    etnia = models.CharField(max_length=2, verbose_name='Etnia', null=True, blank=True)
    nacimiento_pais = models.CharField('Pais Nacimiento', max_length=3, blank=True, null=True)
    nacimiento_departamento = models.CharField('Departamento Nacimiento', max_length=2, blank=True, null=True)
    nacimiento_provincia = models.CharField('Provincia Nacimiento', max_length=4, blank=True, null=True)
    nacimiento_distrito = models.CharField('Distrito Nacimiento', max_length=6, blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=15, blank=True, null=True)
    celular = models.CharField('Celular', max_length=9, blank=True, null=True)
    correo = models.EmailField('Correo electrónico', max_length=70, blank=True, null=True)
    foto = models.TextField(null=True, blank=True)
    uid_cnv = models.CharField('Nº de Documento', max_length=48, blank=True, null=True)
    numero_documento_cnv = models.CharField('Nº de Documento CNV', max_length=12, blank=True, null=True)
    numero_documento_madre = models.CharField('Nº de Documento Madre', max_length=12, blank=True, null=True)
    tipo_documento_madre = models.CharField(
        'Tipo de Documento Madre',
        choices=constants.TDOC_CHOICES,
        max_length=2,
        blank=True,
        null=True
    )
    hora_nacimiento = models.TimeField('Hora de nacimiento', blank=True, null=True)
    cnv_activo = models.BooleanField('Activo CNV', default=False)
    recibesms = models.BooleanField('Recibe SMS', default=False)
    mensaje_personal = models.CharField(max_length=240, null=True, blank=True)
    creator = models.CharField(max_length=20, null=True, blank=True)
    modifier = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    residencia_actual_pais = models.CharField('Pais Actual', max_length=3, blank=True, null=True)
    residencia_actual_departamento = models.CharField('Departamento Actual', max_length=2, blank=True, null=True)
    residencia_actual_provincia = models.CharField('Provincia Actual', max_length=4, blank=True, null=True)
    residencia_actual_distrito = models.CharField('Distrito Actual', max_length=6, blank=True, null=True)
    centro_poblado_actual = models.CharField('Centro Poblado Actual', max_length=12, blank=True, null=True)
    direccion_actual = models.CharField('Dirección Actual', max_length=100, null=True)
    referencia_actual = models.CharField('Referencia Actual', max_length=100, null=True)
    latitud = models.FloatField('Latitud', max_length=100, default='-12.046374', null=True)
    longitud = models.FloatField('Longitud', max_length=100, default='-77.0427934', null=True)

    tipo_abordaje = models.CharField(
        'Paciente abordaje',
        choices=constants.PACIENTE_VIH,
        max_length=10,
        default=constants.TAMIZAJE_WEB
    )

    nombre_social = models.CharField('Nombre social', max_length=100, blank=True)
    poblacion = models.ForeignKey('Poblacion', null=True)
    sin_documento_uuid = models.CharField('Sin documento uuid', max_length=100, blank=True)
    sin_documento_estado = models.BooleanField('Estado sin documento', default=False)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        unique_together = ('tipo_documento', 'numero_documento')

    def __unicode__(self):
        return '{nombre_completo}'.format(nombre_completo=self.nombre_completo)

    def __str__(self):
        return str(self.pk)

    @property
    def nombre_completo(self):
        return '{nombres} {a_paterno} {a_materno}'.format(
            nombres=self.nombres,
            a_paterno=self.apellido_paterno,
            a_materno=self.apellido_materno
        )

    @property
    def is_mostrar_paciente(self):
        if self.cnv_activo and self.tipo_documento == '00':
            return True
        elif self.cnv_activo is False and self.tipo_documento == '00':
            return False
        elif self.tipo_documento != '00':
            return True
        else:
            return False

    @property
    def edad(self):
        age = ''
        if self.fecha_nacimiento:
            today = date.today()
            try:
                birthday = self.fecha_nacimiento.replace(year=today.year)
            except ValueError:
                birthday = self.fecha_nacimiento.replace(year=today.year, day=self.fecha_nacimiento.day - 1)
            age = today.year - self.fecha_nacimiento.year
            if birthday > today:
                age -= 1
        return age

    @property
    def edad_str(self):
        edad = relativedelta(timezone.now().date(), self.fecha_nacimiento)
        txt_anios = '{} {}'.format(edad.years or 0, edad.years == 1 and 'año' or 'años')
        txt_meses = '{} {}'.format(edad.months or 0, edad.months == 1 and 'mes' or 'meses')
        txt_dias = '{} {}'.format(edad.days or 0, edad.days == 1 and 'día' or 'días')
        txt_tiempo = '{}, {}, {}.'.format(txt_anios, txt_meses, txt_dias)
        return txt_tiempo

    @property
    def edad_anios(self):
        return self.edad.years

    @property
    def edad_meses(self):
        return self.edad.months

    @property
    def edad_dias(self):
        return self.edad.days

    @classmethod
    def buscar_paciente(cls, numero_documento, tipo_documento):
        paciente = Paciente.objects.filter(
            numero_documento=numero_documento,
            tipo_documento=tipo_documento
        ).first()
        if paciente:
            if not paciente.sin_documento_estado:
                data = {
                    'uid': paciente.paciente,
                    'apellido_materno': paciente.apellido_materno,
                    'apellido_paterno': paciente.apellido_paterno,
                    'nombres': paciente.nombres,
                    'tipo_documento': paciente.tipo_documento,
                    'numero_documento': paciente.numero_documento,
                    'edad': paciente.edad_str,
                    'etnia': paciente.etnia,
                    'sexo': paciente.sexo,
                    'nombre_social': paciente.nombre_social,
                    'poblacion': paciente.poblacion.id,
                    'fecha_nacimiento': paciente.fecha_nacimiento,
                    'telefono': paciente.telefono,
                    'correo': paciente.correo
                }
                msg = 'Paciente encontrado con éxito'
                return data, msg
            else:
                msg = 'No se encontró el paciente'

                return None, msg
        else:
            try:
                ciudadano = CiudadanoClient(settings.MPI_API_TOKEN).ver(
                    numero_documento,
                    tipo_documento)
                if 'error' not in ciudadano.keys():
                    data = {
                        'uid': ciudadano['uuid'],
                        'apellido_materno': ciudadano.get('apellido_materno', ''),
                        'apellido_paterno': ciudadano.get('apellido_paterno', ''),
                        'nombres': ciudadano.get('nombres', ''),
                        'tipo_documento': ciudadano['tipo_documento'],
                        'numero_documento': ciudadano['numero_documento'],
                        'etnia': ciudadano.get('etnia', ''),
                        'sexo': ciudadano.get('sexo', ''),
                        'edad': ciudadano.get('edad_str', ''),
                        'nombre_social': '',
                        'fecha_nacimiento': ciudadano.get('fecha_nacimiento', ''),
                        'telefono': ciudadano.get('telefono', ''),
                        'correo': ciudadano.get('correo', '')
                    }
                    msg = 'Paciente encontrado con éxito'
                    return data, msg
                else:
                    msg = 'Documento de Identidad no encontrado en MPI'
                    return None, msg
            except Exception as e:
                return None, str(e)


class Poblacion(models.Model):
    denominacion = models.CharField(max_length=250, blank=True)
    movil = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Poblaciones'

    def __str__(self):
        return self.denominacion


class CatalogoEstablecimiento(models.Model):
    codigo_renipres = models.CharField('Código Renipres', max_length=8, unique=True)
    nombre = models.CharField('nombre', max_length=150)
    ubigeo = models.CharField(verbose_name='ubigeo', max_length=8, blank=True, null=True)
    categoria_cod = models.CharField(max_length=10, null=True)
    sector_codigo = models.IntegerField(null=True)
    diresa = models.IntegerField(null=True)
    red = models.IntegerField(null=True)
    cod_red = models.CharField(max_length=2, null=True)
    microred = models.IntegerField(null=True)
    latitude = models.CharField(max_length=15, null=True)
    longitude = models.CharField(max_length=15, null=True)
    nombre_diresa = models.CharField('Nombre DISA/DIRESA', max_length=150, null=True)
    nombre_red = models.CharField('Nombre Red', max_length=150, null=True)
    nombre_microred = models.CharField('Nombre Microred', max_length=150, null=True)
    nombre_sector = models.CharField('Nombre Sector', max_length=150, null=True)

    class Meta:
        verbose_name = 'Establecimiento'
        verbose_name_plural = 'Establecimientos'
        ordering = ('nombre',)

    def __str__(self):
        return self.nombre


class HCE(models.Model):
    paciente = models.ForeignKey('Paciente')
    establecimiento = models.ForeignKey(CatalogoEstablecimiento)
    numero_hce = models.CharField('Nº de Historia Clínica', max_length=12, blank=True, null=True)
    archivo_clinico = models.CharField('Nº Archivo Clinico', max_length=25, blank=True, null=True)
    creator = models.CharField(max_length=20, null=True, blank=True)
    modifier = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('paciente', 'establecimiento')


class PacienteFinanciador(models.Model):
    paciente = models.ForeignKey('Paciente')
    codigo_afiliacion = models.CharField('Nº de Afiliacion', max_length=15)
    estado = models.BooleanField('Estado', default=True)
    tipo_seguro = models.CharField(
        'Tipo Seguro',
        choices=constants.FINANCIADOR_CHOICES,
        max_length=2,
        blank=True, null=True
    )
    regimen = models.CharField('Regimen', choices=constants.REGIMEN_CHOICES, max_length=2, blank=True, null=True)


class PacienteContactoFamiliar(models.Model):
    paciente = models.ForeignKey('Paciente')
    id_phr_familiar = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    tipo_documento = models.CharField(
        'Tipo de Documento', choices=constants.TDOC_CHOICES, max_length=2, blank=True, null=True)
    numero_documento = models.CharField('Nº de documento', max_length=12)
    nombres = models.CharField('Nombres', max_length=100)
    apellido_paterno = models.CharField('Apellido Paterno', max_length=50)
    apellido_materno = models.CharField('Apellido Materno', max_length=50)
    sexo = models.CharField('Sexo', choices=constants.SEXO_CHOICES, max_length=12, blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=15, blank=True, null=True)
    celular = models.CharField('Celular', max_length=12, blank=True, null=True)
    correo = models.EmailField('Correo electrónico', max_length=70, blank=True, null=True)
    parentesco = models.CharField(
        'Parentesco',
        choices=constants.PARENTESCO_CHOICES,
        max_length=2,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Familia'
        verbose_name_plural = 'Familiares'
        unique_together = ('paciente', 'tipo_documento', 'numero_documento')

    def __unicode__(self):
        return '{nombre_completo}'.format(nombre_completo=self.nombre_completo)

    @property
    def nombre_completo(self):
        return '{nombres} {apellido_paterno} {apellido_materno}'.format(
            nombres=self.nombres,
            apellido_paterno=self.apellido_paterno,
            apellido_materno=self.apellido_materno
        )


class UsuarioBrigada(models.Model):
    usuario_name = models.CharField('Usuario login', max_length=15, blank=False, null=False)
    brigada = models.ForeignKey('Brigada')
    establecimiento = models.CharField(verbose_name='Establecimiento', max_length=10, blank=False, null=False)
    ups = models.CharField(verbose_name='UPS', max_length=10, blank=False)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ('usuario_name',)

    def __str__(self):
        return self.usuario_name


class Brigada(models.Model):
    nombre = models.CharField('Nombre', max_length=40)
    ubigeo_departamento = models.CharField(verbose_name='Ubigeo Departamento', max_length=2, blank=True, null=False)
    ubigeo_provincia = models.CharField(verbose_name='Ubigeo Provincia', max_length=4, blank=True, null=False)
    ubigeo_distrito = models.CharField(verbose_name='Ubigeo Distrito', max_length=6, blank=True, null=False)
    nombre_departamento = models.CharField(verbose_name='Nombre de Departamento', max_length=30, blank=True)
    nombre_provincia = models.CharField(verbose_name='Nombre de Provincia', max_length=30, blank=True)
    nombre_distrito = models.CharField(verbose_name='Nombre de Distrito', max_length=30, blank=True)

    class Meta:
        verbose_name = 'Brigada'
        verbose_name_plural = 'Brigadas'
        ordering = ('nombre',)

    def __str__(self):
        return self.nombre


class ATLugarAbordaje(models.Model):
    brigada = models.ForeignKey('Brigada')
    lugar_abordaje = models.ForeignKey('LugarAbordaje')
    detalle = models.CharField('Detalle', max_length=50, blank=True)
    fecha_abordaje = models.DateTimeField(blank=False)
    distrito_lugar_abordaje = models.CharField('Distrito de lugar de Abordaje', max_length=20, blank=False)
    nombre_lugar = models.CharField('Nombre de lugar', max_length=100, blank=True)
    latitud = models.FloatField('Latitud', max_length=100, blank=False)
    longitud = models.FloatField('Longitud', max_length=100, blank=False)

    class Meta:
        verbose_name = 'Atencion'
        verbose_name_plural = 'Atenciones'
        ordering = ('lugar_abordaje',)

    def __str__(self):
        return self.lugar_abordaje


class LugarAbordaje(models.Model):
    nombre = models.CharField('Nombre lugar Abordaje', blank=False, max_length=15, unique=True)
    estado = models.BooleanField('Estado lugar de Abordaje', default=False)

    class Meta:
        verbose_name = 'Lugar abordaje'
        verbose_name_plural = 'Lugares abordaje'
        ordering = ('nombre',)

    def __str__(self):
        return self.nombre


class PacienteLugarAbordaje(models.Model):
    lugar_abordaje = models.ForeignKey('ATLugarAbordaje')
    paciente = models.ForeignKey('Paciente')

    class Meta:
        verbose_name = 'Paciente lugar abordaje '
        verbose_name_plural = 'Paciente lugar abordajes'
        ordering = ('paciente',)

    def __str__(self):
        return self.paciente


class Establecimiento(models.Model):
    diresa = models.CharField('Diresa', max_length=30)
    codigo_ipress = models.CharField('Código IPRESS', max_length=30)
    categorizacion = models.CharField('Categorización', max_length=30)
    tipo = models.CharField('Tipo', max_length=10)
    condicion = models.CharField('Condición', max_length=30)
    establecimiento_salud = models.CharField('Establecimiento de Salud', max_length=200)
    amp = models.CharField('AMP', max_length=30)
    pediatria = models.CharField('Pediatria', max_length=20)
    hepatitis_b = models.CharField('Hepatitis B', max_length=2)

    class Meta:
        verbose_name = 'Establecimiento'
        verbose_name_plural = 'Establecimientos'

    def __str__(self):
        return self.establecimiento_salud
