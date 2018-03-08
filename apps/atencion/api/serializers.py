from rest_framework import serializers
from apps.atencion.models import Atencion, AtencionDiagnostico, AtencionTratamiento
from apps.common.functions import consulta_servicio_ciudadano_uuid, consulta_servicio_ciudadano_datos_sis_uuid
from apps.afiliacion.models import Paciente
from apps.medicamentos.api.serializers import MedicamentoSerializer
from rest_framework.exceptions import NotFound

from django.utils import timezone


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = (
            'nombres', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'nombre_completo', 'edad_str',
            'etnia', 'paciente', 'tipo_documento', 'numero_documento',
            'sexo', 'foto'
        )


class AtencionTratamientoSerializer(serializers.ModelSerializer):
    medicamento = MedicamentoSerializer()

    class Meta:
        model = AtencionTratamiento
        fields = '__all__'


class AtencionDiagnosticoSerializer(serializers.ModelSerializer):
    # cie = CIESerializer()

    class Meta:
        model = AtencionDiagnostico
        fields = '__all__'


class DatosPacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = (
            'nombres', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'nombre_completo', 'edad_str',
            'etnia', 'paciente', 'tipo_documento', 'numero_documento',
            'sexo', 'foto'
        )

    @classmethod
    def get_paciente(cls, data):
        uuid_paciente = data.get('paciente')
        buscar_paciente = Paciente.objects.filter(paciente=uuid_paciente)
        if buscar_paciente:
            return Paciente.objects.get(paciente=uuid_paciente)
        else:
            datos_mpi = consulta_servicio_ciudadano_uuid(uuid_paciente)
            if datos_mpi['resultado'] == 'OK':
                return Paciente.objects.get(paciente=datos_mpi['uuid'])
            else:
                raise NotFound


class AtencionSerializer(serializers.ModelSerializer):
    paciente = DatosPacienteSerializer(read_only=True)

    class Meta:
        model = Atencion
        fields = ('eess', 'paciente', 'medico', 'cita', 'fecha')
        read_only_fields = ('fecha', )

    @classmethod
    def get_atencion(cls, data):
        instancia = cls(data=data)
        if instancia.is_valid():
            uuid_paciente = data.get('paciente')
            medico = data.get('medico')
            cita = data.get('cita')
            eess = data.get('eess')
            ups = data.get('ups')
            fecha_actual = timezone.now().date()
            fecha_registro = fecha_actual.strftime("%Y-%m-%d")
            buscar_paciente = Paciente.objects.filter(paciente=uuid_paciente).first()
            buscar_atencion = Atencion.objects.filter(
                paciente=buscar_paciente,
                eess=eess,
                medico=medico,
                cita_uuid=cita,
                ups=ups,
                fecha=fecha_registro
            )
            if buscar_atencion:
                obj = buscar_atencion.first()
                return obj
            else:
                datos_sis = consulta_servicio_ciudadano_datos_sis_uuid(uuid_paciente)
                if datos_sis['estado'] == '1':
                    atencion = Atencion()
                    atencion.paciente = buscar_paciente
                    atencion.eess = eess
                    atencion.medico = medico
                    atencion.cita_uuid = cita
                    atencion.ups = ups
                    atencion.fecha = fecha_registro
                    atencion.id_financiador = '2'
                    atencion.contrato = datos_sis['contrato']
                    atencion.tipo_seguro = datos_sis['tiposeguro']
                    atencion.tipo_seguro_descripcion = datos_sis['descripcion_tiposeguro']
                    atencion.regimen = datos_sis['regimen']
                    atencion.codigo_eess = datos_sis['codigo_eess']
                    atencion.nombre_eess = datos_sis['nom_eess']
                    atencion.tipo_atencion = 1
                    atencion.estado_cita = 2
                    atencion.estado_atencion = 2
                    atencion.save()
                    return atencion
                else:
                    atencion = Atencion()
                    atencion.paciente = uuid_paciente
                    atencion.eess = eess
                    atencion.medico = medico
                    atencion.cita_uuid = cita
                    atencion.ups = ups
                    atencion.fecha = fecha_registro
                    atencion.id_financiador = '0'
                    atencion.contrato = ''
                    atencion.tipo_seguro = ''
                    atencion.tipo_seguro_descripcion = ''
                    atencion.regimen = ''
                    atencion.codigo_eess = ''
                    atencion.nombre_eess = ''
                    atencion.tipo_atencion = 1
                    atencion.estado_cita = 2
                    atencion.estado_atencion = 2
                    atencion.save()
                    return atencion
