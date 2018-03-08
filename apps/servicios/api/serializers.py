from django.conf import settings
from django.utils import timezone
from mpi_client.client import CiudadanoClient
from rest_framework import serializers

from apps.afiliacion.models import ATLugarAbordaje, Brigada, LugarAbordaje, Paciente, Poblacion, UsuarioBrigada
from apps.atencion.models import Atencion
from apps.common import constants
from apps.consejeria.models import Consejeria, ConsejeriaPre
from apps.laboratorio.models import Examen, ExamenResultado


class BrigadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brigada
        fields = ('id', 'nombre', 'ubigeo_distrito', 'nombre_distrito')


class LugarAbordajeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LugarAbordaje
        fields = ('id', 'nombre', 'estado')


class ATLugarAbordajeSerializer(serializers.ModelSerializer):

    brigada = BrigadaSerializer(read_only=True)
    lugar_abordaje = LugarAbordajeSerializer(read_only=True)

    class Meta:
        model = ATLugarAbordaje
        fields = ('id', 'brigada', 'lugar_abordaje', 'detalle', 'fecha_abordaje')


class BrigadaUsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsuarioBrigada
        fields = (
            'brigada', 'establecimiento', 'ups'
        )


class PacientesLugarAbordaje(serializers.ModelSerializer):

    fecha_abordaje = serializers.DateField(write_only=True, required=True)

    class Meta:
        model = ATLugarAbordaje
        fields = (
            'id', 'brigada', 'lugar_abordaje', 'detalle', 'fecha_abordaje', 'distrito_lugar_abordaje',
            'nombre_lugar', 'latitud', 'longitud'
        )

    def validate_fecha_abordaje(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError('No se puede registrar una fecha mayor a la fecha actual')
        return value

    def create(self, validated_data):
        # Si el lugar de Abordaje es 'Otros' se llena Detalle
        if validated_data['lugar_abordaje'].id == LugarAbordaje.objects.get(nombre=constants.LUGAR_ABORDAJE_OTRO):
            detalle = validated_data.get('detalle')
        else:
            detalle = ''

        validated_data["detalle"] = detalle
        return super().create(validated_data)


class PoblacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poblacion
        fields = (
            'id', 'denominacion', 'movil'
        )


class PacientePoblacionSerializer(serializers.ModelSerializer):
    paciente_sin_documento = serializers.CharField(read_only=True)

    class Meta:
        model = Paciente
        fields = (
            'paciente_sin_documento', 'paciente', 'sexo', 'fecha_nacimiento', 'etnia', 'telefono', 'correo',
            'tipo_documento',
            'numero_documento', 'apellido_paterno', 'apellido_materno', 'nombres', 'nombre_social',
            'poblacion', 'sin_documento_uuid', 'sin_documento_estado'
        )


class AtencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atencion
        fields = ('eess', 'medico', 'paciente', 'cita_uuid', 'ups', 'fecha')


class ConsejeriaPreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsejeriaPre
        fields = ('consejeria', 'tipo_poblacion', 'consejeria_previa', 'esta_consentido')


class ConsejeriaExamenSerializer(serializers.ModelSerializer):

    atencion = AtencionSerializer(read_only=True)
    consejeria = ConsejeriaPreSerializer(read_only=True)
    tipo_poblacion_id = serializers.IntegerField(write_only=True)
    fecha_prueba = serializers.DateField(write_only=True)
    esta_consentido = serializers.BooleanField(write_only=True)
    lugar_abordaje = serializers.IntegerField(write_only=True)

    class Meta:
        model = Examen
        fields = (
            'atencion',
            'consejeria',
            'consejeria_pre',
            'lugar_abordaje',
            'eess', 'observaciones', 'fecha_prueba',  'cpt', 'personal_salud', 'hora_solicitud', 'codigo_muestra',
            'codigo_qr', 'tipo_poblacion_id', 'esta_consentido', 'paciente', 'nombre'

        )

    def validate_codigo_qr(self, value):
        if Examen.objects.filter(codigo_qr=value).exists():
            raise serializers.ValidationError('El código QR ya existe')
        return value

    def create(self, validated_data):

        atencion_paciente = Atencion.objects.filter(
            paciente=validated_data.get('paciente'), fecha=validated_data.get('fecha_prueba'),
            ups='1094', eess=validated_data.get('eess'), medico=validated_data.get('personal_salud')).first()
        if atencion_paciente:
            consejeria = Consejeria.objects.create(
                atencion=atencion_paciente,
                tipo_consejeria=constants.PRE,
                fecha_registro=validated_data.get('fecha_registro')
            )
            ConsejeriaPre.objects.create(
                consejeria=consejeria,
                tipo_poblacion=Poblacion.objects.get(id=validated_data.get('tipo_poblacion_id')),
                consejeria_previa=True,
                esta_consentido=validated_data.get('esta_consentido'),
                validacion=''
            )
            examen = Examen.objects.create(
                paciente=validated_data.get('paciente'),
                consejeria_pre=consejeria,
                eess=validated_data.get('eess'),
                observaciones=validated_data.get('observaciones'),
                fecha_prueba=validated_data.get('fecha_prueba'),
                cpt=validated_data.get('cpt'),
                personal_salud=validated_data.get('personal_salud'),
                codigo_muestra=validated_data.get('codigo_muestra'),
                codigo_qr=validated_data.get('codigo_qr'),
                hora_solicitud=validated_data.get('hora_solicitud'),
                nombre=validated_data.get('nombre'),
            )

            return examen

        else:
            try:
                lugar_abordaje = ATLugarAbordaje.objects.get(id=validated_data.get('lugar_abordaje'))
            except ATLugarAbordaje.DoesNotExist:
                lugar_abordaje = None

            atencion = Atencion.objects.create(
                paciente=Paciente.objects.get(paciente=validated_data.get('paciente')),
                cita_uuid=None,
                fecha=validated_data.get('fecha_prueba'),
                ups='1094',
                eess=validated_data.get('eess'),
                medico=validated_data.get('personal_salud'),
                tipo_registro=constants.TAMIZAJE_WEB,
                lugar_abordaje=lugar_abordaje
            )
            consejeria = Consejeria.objects.create(
                atencion=atencion,
                tipo_consejeria=constants.PRE,
                fecha_registro=validated_data.get('fecha_registro')
            )

            ConsejeriaPre.objects.create(
                consejeria=consejeria,
                tipo_poblacion=Poblacion.objects.get(id=validated_data.get('tipo_poblacion_id')),
                consejeria_previa=True,
                esta_consentido=validated_data.get('esta_consentido'),
                validacion=''
            )

            examen = Examen.objects.create(
                paciente=validated_data.get('paciente'),
                consejeria_pre=consejeria,
                eess=validated_data.get('eess'),
                observaciones=validated_data.get('observaciones'),
                fecha_prueba=validated_data.get('fecha_prueba'),
                cpt=validated_data.get('cpt'),
                personal_salud=validated_data.get('personal_salud'),
                codigo_muestra=validated_data.get('codigo_muestra'),
                codigo_qr=validated_data.get('codigo_qr'),
                hora_solicitud=validated_data.get('hora_solicitud'),
                nombre=validated_data.get('nombre'),
            )

            return examen


class ResultadosExamenesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenResultado
        fields = (
            'id', 'laboratorio_examen', 'resultado', 'nro_prueba', 'nro_muestra', 'fecha_resultado', 'observacion',
            'post_test',
            'ficha_informativa', 'refiere_eess', 'codigo_eess', 'nombre_eess', 'fecha_cita', 'fecha_registro',
            'repite_prueba', 'cantidad_condones', 'cantidad_lubricantes'
        )


class ListadoExamenesSerializer(serializers.ModelSerializer):
    examen_resultado = ResultadosExamenesSerializer(read_only=True)

    class Meta:
        model = Examen
        fields = ('id', 'fecha_prueba', 'personal_salud', 'codigo_qr', 'nombre', 'cpt', 'examen_resultado')


class ExamenResultadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenResultado
        fields = (
            'id', 'laboratorio_examen', 'resultado', 'nro_prueba', 'nro_muestra', 'fecha_resultado', 'observacion',
            'post_test',
            'ficha_informativa', 'refiere_eess', 'codigo_eess', 'nombre_eess', 'fecha_cita', 'fecha_registro',
            'repite_prueba', 'cantidad_condones', 'cantidad_lubricantes'
        )


class ExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = (
            'consejeria_pre', 'personal_salud', 'eess', 'estado', 'observaciones', 'fecha_prueba', 'codigo_muestra',
            'codigo_qr', 'hora_solicitud', 'nombre',
        )


class ExamenBuscarQrSerializer(serializers.ModelSerializer):
    laboratorio_examen = ExamenSerializer(read_only=True)

    class Meta:
        model = ExamenResultado
        fields = (
            'id', 'laboratorio_examen', 'resultado', 'nro_prueba', 'nro_muestra', 'fecha_resultado', 'observacion',
            'post_test',
            'ficha_informativa', 'refiere_eess', 'codigo_eess', 'nombre_eess', 'fecha_cita', 'fecha_registro',
            'repite_prueba', 'cantidad_condones', 'cantidad_lubricantes'
        )


class PacienteSerializer(serializers.ModelSerializer):

    class Meta:

        model = Paciente
        fields = (
            'sexo', 'fecha_nacimiento', 'etnia', 'telefono', 'correo', 'apellido_paterno',
            'apellido_materno', 'nombres', 'nombre_social', 'poblacion', 'numero_documento'
        )
        extra_kwargs = {
            'numero_documento': {'required': False}
        }

    def create(self, validated_data):
        mpi_client = CiudadanoClient(settings.MPI_API_TOKEN)
        data = {
                "nombres": validated_data.get('nombres'),
                "apellido_materno": validated_data.get('apellido_materno'),
                "apellido_paterno": validated_data.get('apellido_paterno'),
                "nombre_social": validated_data.get('nombre_social'),
                "sexo": validated_data.get('sexo'),
                "poblacion": validated_data.get('poblacion'),
                "correo": validated_data.get('correo'),
                "eess": validated_data.get('eess'),
                "etnia": validated_data.get('etnia'),
                "fecha_nacimiento": validated_data.get('fecha_nacimiento'),
                "telefono": validated_data.get('telefono'),
                'tipo_documento': constants.TIPO_SIN_DOCUMENTO,
                'numero_documento': ''
            }

        datos_paciente = mpi_client.crear_sin_documento(data=data)
        if 'error' not in datos_paciente and 'errors' not in datos_paciente:
            datos_paciente = datos_paciente.get('data').get('attributes')
            validated_data['paciente'] = datos_paciente.get('uuid', '')
            validated_data['numero_documento'] = datos_paciente.get('numero_documento', '')
            validated_data['tipo_documento'] = datos_paciente.get('tipo_documento', '')
            return super().create(validated_data)
        else:
            serializers.ValidationError('Ha ocurrido un error al registrar al paciente')


class UsuarioBrigadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioBrigada
        fields = ('id', 'usuario_name', 'establecimiento', 'ups', 'brigada')


class SincronizacionPacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = (
            'paciente', 'nombres', 'apellido_paterno', 'apellido_materno', 'correo', 'etnia', 'fecha_nacimiento',
            'numero_documento', 'sexo', 'tipo_documento', 'nombre_social', 'poblacion'
        )


class SincronizacionAtencionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Atencion
        fields = (
            'paciente', 'medico', 'cita_uuid', 'fecha', 'ups', 'tipo_registro', 'lugar_abordaje',
            'tipo_registro', 'eess')


class SincronizacionConsejeriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consejeria
        fields = (
            'atencion', 'tipo_consejeria', 'fecha_registro'
        )


class SincronizacionConsejeriaPreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsejeriaPre
        fields = (
            'consejeria', 'tipo_poblacion', 'consejeria_previa', 'esta_consentido', 'validacion'
        )


class SincronizacionAtencionLugarAbordaje(serializers.ModelSerializer):
    fecha_abordaje = serializers.DateField(write_only=True)

    class Meta:
        model = ATLugarAbordaje
        fields = (
             "fecha_abordaje", "distrito_lugar_abordaje", "nombre_lugar", "brigada", "lugar_abordaje", "latitud",
             "longitud"
        )


class SincronizarExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = (
            'paciente', 'consejeria_pre', 'personal_salud', 'eess', 'estado', 'observaciones', 'fecha_prueba',
            'codigo_muestra', 'codigo_qr', 'hora_solicitud', 'nombre', 'consejeria_pre_id'
        )
