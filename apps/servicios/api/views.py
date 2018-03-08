import logging

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import View
from mpi_client.client import MPIClient
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.afiliacion.models import ATLugarAbordaje, Brigada, LugarAbordaje, Paciente, Poblacion, UsuarioBrigada, \
    Establecimiento
from apps.atencion.models import Atencion
from apps.common import constants
from apps.common.authentication import APITokenAuthentication
from apps.laboratorio.models import Examen, ExamenResultado
from .serializers import (
    ATLugarAbordajeSerializer, BrigadaSerializer, BrigadaUsuarioSerializer,
    ConsejeriaExamenSerializer, ExamenBuscarQrSerializer, ExamenResultadoSerializer, LugarAbordajeSerializer,
    PacientePoblacionSerializer, PacienteSerializer, PacientesLugarAbordaje,
    PoblacionSerializer, UsuarioBrigadaSerializer, SincronizacionPacienteSerializer, SincronizacionAtencionSerializer,
    SincronizacionAtencionLugarAbordaje, SincronizacionConsejeriaSerializer, SincronizacionConsejeriaPreSerializer,
    SincronizarExamenSerializer)
from mpi_client.client import CiudadanoClient
from django.db.models import Q
logger = logging.getLogger(__name__)


class BrigadaDataView(generics.ListAPIView):
    serializer_class = BrigadaSerializer
    model = Brigada
    queryset = Brigada.objects.all()
    authentication_classes = (APITokenAuthentication,)


class LugarAbordajeView(generics.ListAPIView):
    serializer_class = LugarAbordajeSerializer
    model = LugarAbordaje
    queryset = LugarAbordaje.objects.all().order_by('id')
    authentication_classes = (APITokenAuthentication,)


class ATlugarAbordajeView(generics.ListAPIView):
    serializer_class = ATLugarAbordajeSerializer
    model = ATLugarAbordaje
    queryset = ATLugarAbordaje.objects.all()
    authentication_classes = (APITokenAuthentication,)


class DistritoDataView(View):
    #authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):
        lugar_id = self.kwargs.get('ubig_prov')
        dep_id = lugar_id[0:2]
        prov_id = lugar_id
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/{}/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id, prov_id)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        {'ubigeo': obj['attributes']['cod_ubigeo_inei_distrito'],
                            'nombre': obj['attributes']['ubigeo_distrito']})

            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return JsonResponse({'data': lista_data})


class ProvinciaDataView(View):
    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):

        lista_data = []
        try:
            mpi_client = MPIClient(settings.MPI_API_TOKEN)
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            dep_id = self.kwargs.get('ubig_departamento')
            response = mpi_client.get('{}/api/v1/ubigeo/1/177/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id),
                                      headers=headers)

            if response.status_code == 200:
                data = response.json()['data'] if response.json()['data'] else []
                for obj in data:
                    lista_data.append({
                        'ubigeo': obj['attributes']['cod_ubigeo_inei_provincia'],
                        'nombre': obj['attributes']['ubigeo_provincia']
                    })
            else:
                lista_data = []
        except Exception as e:
            logger.warning('Error al conectar con MPI', exc_info=True)
            lista_data = []
        return JsonResponse({'data': lista_data})


class PoblacionDataView(generics.ListAPIView):
    serializer_class = PoblacionSerializer
    model = Poblacion
    queryset = Poblacion.objects.filter(movil=True).order_by('id')
    authentication_classes = (APITokenAuthentication,)


class UsuarioBrigadaCreateView(generics.CreateAPIView):
    serializer_class = BrigadaUsuarioSerializer
    queryset = UsuarioBrigada.objects.all()
    authentication_classes = (APITokenAuthentication,)

    def perform_create(self, serializer):
        serializer.save(usuario_name=self.request.user)


class PacientePoblacionCreateView(generics.CreateAPIView):
    serializer_class = PacientePoblacionSerializer
    queryset = Paciente.objects.all()
    #authentication_classes = (APITokenAuthentication,)

    def post(self, request, *args, **kwargs):
        paciente = Paciente.objects.filter(paciente=self.request.data.get('paciente')).first()
        if paciente is not None:
            paciente_serializer = PacientePoblacionSerializer(paciente, data=request.data)
            if paciente_serializer.is_valid():
                paciente_serializer.save()
                return JsonResponse(paciente_serializer.data, status=200)
            return JsonResponse(paciente_serializer.errors, status=400)
        else:
            if not self.request.data.get('paciente_sin_documento'):
                paciente_serializer = PacientePoblacionSerializer(data=request.data)
                if paciente_serializer.is_valid():
                    paciente_serializer.save()
                    return JsonResponse(paciente_serializer.data, status=200)
                return JsonResponse(paciente_serializer.errors, status=400)
            else:
                Paciente.objects.filter(paciente=self.request.data.get(
                    'paciente_sin_documento')).update(sin_documento_estado=True)

                paciente_serializer = PacientePoblacionSerializer(data=request.data)
                if paciente_serializer.is_valid():
                    paciente_serializer.save()
                    return JsonResponse(paciente_serializer.data, status=200)
                return JsonResponse(paciente_serializer.errors, status=400)


class ATLugarAbordajeCreateView(generics.CreateAPIView):
    serializer_class = PacientesLugarAbordaje
    queryset = ATLugarAbordaje.objects.all()
    #authentication_classes = (APITokenAuthentication,)


class BuscarPaciente(APIView):
    #authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):
        """
            Consulta a WS de MPI para obtener datos del ciudadano

            :param nro_documento: Numero documento del Ciudadano
            :param tipo_documento: Tipo de documento del Ciudadano
            :return: Diccionario con datos obtenidos de consulta a WS de MPI.
            :rtype: dict
        """
        paciente, msg = Paciente.buscar_paciente(
            self.kwargs.get('numero_documento'),
            self.kwargs.get('tipo_documento'))
        if paciente:
            return Response(paciente)
        else:
            return Response(paciente, status.HTTP_404_NOT_FOUND)


class ConsejeriaExamenCreateView(generics.CreateAPIView):
    serializer_class = ConsejeriaExamenSerializer
    queryset = Examen.objects.all()
    #authentication_classes = (APITokenAuthentication,)


class ListExamenesApiView(APIView):

    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):
        paciente = Paciente.objects.filter(paciente=self.kwargs.get('paciente')).first()
        if not paciente.sin_documento_uuid:
            data = []
            examenes = Examen.objects.filter(paciente=self.kwargs.get('paciente')).all()
            for examen in examenes:
                examen_paciente = {
                    "id": examen.id,
                    "consejeria_pre": examen.consejeria_pre.id,
                    "personal_salud": examen.personal_salud,
                    "eess": examen.eess,
                    "estado": examen.estado,
                    "observaciones": examen.observaciones,
                    "fecha_prueba": examen.fecha_prueba,
                    "codigo_muestra": examen.codigo_muestra,
                    "codigo_qr": examen.codigo_qr,
                    "hora_solicitud": examen.hora_solicitud,
                    "nombre": examen.nombre,
                    "cpt": examen.cpt,
                    'resultado_examen': []
                }
                examen_resultado = ExamenResultado.objects.filter(laboratorio_examen=examen).last()
                temp = None
                if examen_resultado:
                    temp = {
                        'id': examen_resultado.id,
                        'resultado': examen_resultado.resultado,
                        'nro_prueba': examen_resultado.nro_prueba,
                        'nro_muestra': examen_resultado.nro_muestra,
                        'fecha_resultado': examen_resultado.fecha_resultado,
                        'observacion': examen_resultado.observacion,
                        'post_test': examen_resultado.post_test,
                        'ficha_informativa': examen_resultado.ficha_informativa,
                        'refiere_eess': examen_resultado.refiere_eess,
                        'codigo_eess': examen_resultado.codigo_eess,
                        'nombre_eess': examen_resultado.nombre_eess,
                        'fecha_cita': examen_resultado.fecha_cita,
                        'fecha_registro': examen_resultado.fecha_registro,
                        'repite_prueba': examen_resultado.repite_prueba,
                        'cantidad_condones': examen_resultado.cantidad_condones,
                        'cantidad_lubricantes': examen_resultado.cantidad_lubricantes,
                    }

                examen_paciente['resultado_examen'] = temp

                data.append(examen_paciente)
            return Response(data)
        else:

            data_old = []
            data_pac = []

            examenes_old = Examen.objects.filter(paciente=paciente.sin_documento_uuid).all()
            for examen in examenes_old:
                examen_paciente = {
                    "id": examen.id,
                    "consejeria_pre": examen.consejeria_pre.id,
                    "personal_salud": examen.personal_salud,
                    "eess": examen.eess,
                    "estado": examen.estado,
                    "observaciones": examen.observaciones,
                    "fecha_prueba": examen.fecha_prueba,
                    "codigo_muestra": examen.codigo_muestra,
                    "codigo_qr": examen.codigo_qr,
                    "hora_solicitud": examen.hora_solicitud,
                    "nombre": examen.nombre,
                    "cpt": examen.cpt,
                    'resultado_examen': []
                }
                examen_resultado = ExamenResultado.objects.filter(laboratorio_examen=examen).last()
                temp = None
                if examen_resultado:
                    temp = {
                        'id': examen_resultado.id,
                        'resultado': examen_resultado.resultado,
                        'nro_prueba': examen_resultado.nro_prueba,
                        'nro_muestra': examen_resultado.nro_muestra,
                        'fecha_resultado': examen_resultado.fecha_resultado,
                        'observacion': examen_resultado.observacion,
                        'post_test': examen_resultado.post_test,
                        'ficha_informativa': examen_resultado.ficha_informativa,
                        'refiere_eess': examen_resultado.refiere_eess,
                        'codigo_eess': examen_resultado.codigo_eess,
                        'nombre_eess': examen_resultado.nombre_eess,
                        'fecha_cita': examen_resultado.fecha_cita,
                        'fecha_registro': examen_resultado.fecha_registro,
                        'repite_prueba': examen_resultado.repite_prueba,
                        'cantidad_condones': examen_resultado.cantidad_condones,
                        'cantidad_lubricantes': examen_resultado.cantidad_lubricantes,
                    }

                examen_paciente['resultado_examen'] = temp

                data_old.append(examen_paciente)

            examenes = Examen.objects.filter(paciente=self.kwargs.get('paciente')).all()
            for examen in examenes:
                examen_paciente = {
                    "id": examen.id,
                    "consejeria_pre": examen.consejeria_pre.id,
                    "personal_salud": examen.personal_salud,
                    "eess": examen.eess,
                    "estado": examen.estado,
                    "observaciones": examen.observaciones,
                    "fecha_prueba": examen.fecha_prueba,
                    "codigo_muestra": examen.codigo_muestra,
                    "codigo_qr": examen.codigo_qr,
                    "hora_solicitud": examen.hora_solicitud,
                    "nombre": examen.nombre,
                    "cpt": examen.cpt,
                    'resultado_examen': []
                }
                examen_resultado = ExamenResultado.objects.filter(laboratorio_examen=examen).last()
                temp = None
                if examen_resultado:
                    temp = {
                        'id': examen_resultado.id,
                        'resultado': examen_resultado.resultado,
                        'nro_prueba': examen_resultado.nro_prueba,
                        'nro_muestra': examen_resultado.nro_muestra,
                        'fecha_resultado': examen_resultado.fecha_resultado,
                        'observacion': examen_resultado.observacion,
                        'post_test': examen_resultado.post_test,
                        'ficha_informativa': examen_resultado.ficha_informativa,
                        'refiere_eess': examen_resultado.refiere_eess,
                        'codigo_eess': examen_resultado.codigo_eess,
                        'nombre_eess': examen_resultado.nombre_eess,
                        'fecha_cita': examen_resultado.fecha_cita,
                        'fecha_registro': examen_resultado.fecha_registro,
                        'repite_prueba': examen_resultado.repite_prueba,
                        'cantidad_condones': examen_resultado.cantidad_condones,
                        'cantidad_lubricantes': examen_resultado.cantidad_lubricantes,
                    }

                examen_paciente['resultado_examen'] = temp

                data_pac.append(examen_paciente)

            data = data_old + data_pac
            return Response(data)


class ExamenesView(generics.ListAPIView):
    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):
        params = {'flag': 'vih', 'dominio': settings.CATALOGO_ODOO_HOST_URL}
        headers = {'Authorization': 'Bearer '+settings.CATALOGO_ODOO_TOKEN, }
        url = "{dominio}/api/catalogominsa.cpt_procedimiento/?flag={flag}".format(**params)

        res = requests.get(url=url, headers=headers)
        lista_examenes = []
        if res.status_code == 200:
            data = res.json()['data']
            for examen in data:
                lista_examenes.append({
                    "codigo": examen["procedimiento_codigo"], "nombre": examen["procedimiento_nombrecorto"]})

        return JsonResponse({'data': lista_examenes})


class CreateExamenResultadoListAPIView(generics.CreateAPIView):
    serializer_class = ExamenResultadoSerializer
    uthentication_classes = (APITokenAuthentication,)


class UpdateExamenResultadoListAPIView(generics.RetrieveUpdateAPIView):
    http_method_names = ['put', ]
    serializer_class = ExamenResultadoSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return ExamenResultado.objects.all()


class BusquedaExamenQrApiView(APIView):
    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = []
        examenes = Examen.objects.filter(codigo_qr=self.kwargs.get('codigo_qr')).all()

        for examen in examenes:
            paciente = Paciente.objects.filter(paciente=examen.paciente).first()
            if not paciente.sin_documento_estado:
                examen_paciente = {
                    "id": examen.id,
                    "uid": paciente.paciente,
                    "nombres": paciente.nombres,
                    "apellido_paterno": paciente.apellido_paterno,
                    "apellido_materno": paciente.apellido_materno,
                    "nombre_social": paciente.nombre_social,
                    "consejeria_pre": examen.consejeria_pre.id,
                    "personal_salud": examen.personal_salud,
                    "eess": examen.eess,
                    "estado": examen.estado,
                    "observaciones": examen.observaciones,
                    "fecha_prueba": examen.fecha_prueba,
                    "codigo_muestra": examen.codigo_muestra,
                    "codigo_qr": examen.codigo_qr,
                    "hora_solicitud": examen.hora_solicitud,
                    "nombre": examen.nombre,
                    'resultado_examen': []
                }
                examen_resultado = ExamenResultado.objects.filter(laboratorio_examen=examen).last()
                temp = None
                if examen_resultado:
                    temp = {
                        'id': examen_resultado.id,
                        'resultado': examen_resultado.resultado,
                        'nro_prueba': examen_resultado.nro_prueba,
                        'nro_muestra': examen_resultado.nro_muestra,
                        'fecha_resultado': examen_resultado.fecha_resultado,
                        'observacion': examen_resultado.observacion,
                        'post_test': examen_resultado.post_test,
                        'ficha_informativa': examen_resultado.ficha_informativa,
                        'refiere_eess': examen_resultado.refiere_eess,
                        'codigo_eess': examen_resultado.codigo_eess,
                        'nombre_eess': examen_resultado.nombre_eess,
                        'fecha_cita': examen_resultado.fecha_cita,
                        'fecha_registro': examen_resultado.fecha_registro,
                        'repite_prueba': examen_resultado.repite_prueba,
                        'cantidad_condones': examen_resultado.cantidad_condones,
                        'cantidad_lubricantes': examen_resultado.cantidad_lubricantes,
                    }

                examen_paciente['resultado_examen'] = temp

                data.append(examen_paciente)
            else:
                paciente_activo = Paciente.objects.filter(sin_documento_uuid=examen.paciente).first()
                examen_paciente = {
                    "id": examen.id,
                    "uid": paciente_activo.paciente,
                    "nombres": paciente_activo.nombres,
                    "apellido_paterno": paciente_activo.apellido_paterno,
                    "apellido_materno": paciente_activo.apellido_materno,
                    "nombre_social": paciente_activo.nombre_social,
                    "consejeria_pre": examen.consejeria_pre.id,
                    "personal_salud": examen.personal_salud,
                    "eess": examen.eess,
                    "estado": examen.estado,
                    "observaciones": examen.observaciones,
                    "fecha_prueba": examen.fecha_prueba,
                    "codigo_muestra": examen.codigo_muestra,
                    "codigo_qr": examen.codigo_qr,
                    "hora_solicitud": examen.hora_solicitud,
                    "nombre": examen.nombre,
                    'resultado_examen': []
                }
                examen_resultado = ExamenResultado.objects.filter(laboratorio_examen=examen).last()
                temp = None
                if examen_resultado:
                    temp = {
                        'id': examen_resultado.id,
                        'resultado': examen_resultado.resultado,
                        'nro_prueba': examen_resultado.nro_prueba,
                        'nro_muestra': examen_resultado.nro_muestra,
                        'fecha_resultado': examen_resultado.fecha_resultado,
                        'observacion': examen_resultado.observacion,
                        'post_test': examen_resultado.post_test,
                        'ficha_informativa': examen_resultado.ficha_informativa,
                        'refiere_eess': examen_resultado.refiere_eess,
                        'codigo_eess': examen_resultado.codigo_eess,
                        'nombre_eess': examen_resultado.nombre_eess,
                        'fecha_cita': examen_resultado.fecha_cita,
                        'fecha_registro': examen_resultado.fecha_registro,
                        'repite_prueba': examen_resultado.repite_prueba,
                        'cantidad_condones': examen_resultado.cantidad_condones,
                        'cantidad_lubricantes': examen_resultado.cantidad_lubricantes,
                    }

                examen_paciente['resultado_examen'] = temp

                data.append(examen_paciente)
        return Response(data)


class BusquedaExamenResultadoView(generics.ListAPIView):
    serializer_class = ExamenBuscarQrSerializer
    authentication_classes = (APITokenAuthentication,)

    def get_queryset(self):
        examen_resultado = ExamenResultado.objects.filter(laboratorio_examen_id=self.kwargs.get('id_examen'))
        return examen_resultado


class PacienteCreateView(generics.CreateAPIView):
    serializer_class = PacienteSerializer
    authentication_classes = (APITokenAuthentication,)


class ObtenerBrigadaView(APIView):
    authentication_classes = (APITokenAuthentication, )
    serializer_class = UsuarioBrigadaSerializer

    def get(self, request, usuario):
        ultima_brigada = UsuarioBrigada.objects.filter(
                usuario_name=usuario).order_by('id').last()
        if ultima_brigada is None:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = UsuarioBrigadaSerializer(ultima_brigada)
            return Response(serializer.data)


class ObtenerTamizajeView(APIView):
    authentication_classes = (APITokenAuthentication, )

    def get(self, request, *args, **kwargs):
        try:
            brigada = Brigada.objects.get(id=self.kwargs.get('id_brigada'))
            atenciones = Atencion.objects.filter(lugar_abordaje__brigada=brigada).all()
            data = []
            for atencion in atenciones:
                if atencion:
                    data_paciente = {
                        'uid': atencion.paciente.paciente,
                        'nombres': atencion.paciente.nombres,
                        'apellido_paterno': atencion.paciente.apellido_paterno,
                        'apellido_materno': atencion.paciente.apellido_materno,
                        'correo': atencion.paciente.correo,
                        'etnia': atencion.paciente.etnia,
                        'numero_documento': atencion.paciente.numero_documento,
                        'tipo_documento': atencion.paciente.tipo_documento,
                        'poblacion': atencion.paciente.poblacion_id,
                        'nombre_social': atencion.paciente.nombre_social,
                        'fecha_nacimiento': atencion.paciente.fecha_nacimiento,
                        'sexo': atencion.paciente.sexo,
                        'examenes': []
                    }

                    examenes = Examen.objects.filter(consejeria_pre__atencion=atencion).all()
                    data_examen = []
                    for examen in examenes:
                        if examen:
                            temp_examen = {
                                "id": examen.id,
                                "consejeria_pre": examen.consejeria_pre.id,
                                "personal_salud": examen.personal_salud,
                                "eess": examen.eess,
                                "estado": examen.estado,
                                "observaciones": examen.observaciones,
                                "fecha_prueba": examen.fecha_prueba,
                                "codigo_muestra": examen.codigo_muestra,
                                "codigo_qr": examen.codigo_qr,
                                "hora_solicitud": examen.hora_solicitud,
                                "nombre": examen.nombre,
                                "cpt": examen.cpt,
                                "resultado_examen": None
                            }

                            examen_resultado = ExamenResultado.objects.filter(
                                laboratorio_examen=examen).first()

                            if examen_resultado:
                                resultados_examenes = {
                                    'id': examen_resultado.id,
                                    'nombre_eess': examen_resultado.nombre_eess,
                                    'observacion': examen_resultado.observacion,
                                    'resultado': examen_resultado.resultado,
                                    'fecha_resultado': examen_resultado.fecha_resultado,
                                    'cantidad_condones': examen_resultado.cantidad_condones,
                                    'cantidad_lubricantes': examen_resultado.cantidad_lubricantes,
                                    'fecha_registro': examen_resultado.fecha_registro,
                                    'fecha_cita': examen_resultado.fecha_cita,
                                    'nro_prueba': examen_resultado.nro_prueba,
                                    'nro_muestra': examen_resultado.nro_muestra
                                }

                                temp_examen["resultado_examen"] = resultados_examenes
                        data_examen.append(temp_examen)
                    data_paciente["examenes"] = data_examen
                    data.append(data_paciente)

            return Response(data)
        except Brigada.DoesNotExist:
            return Response([])


class SincronizarDatosView(APIView):
    authentication_classes = (APITokenAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        data_usuario_brigada = {
            'usuario_name': data.get('paciente').get('personal_salud'),
            'brigada': data.get('at_lugar_abordaje').get('brigada'),
            'establecimiento': data.get('paciente').get('eess'),
            'ups': data.get('paciente').get('ups')
        }
        serializer_usuario_brigada = UsuarioBrigadaSerializer(data=data_usuario_brigada)
        serializer_usuario_brigada.is_valid(raise_exception=True)
        serializer_usuario_brigada.save()

        serializer_at_lugar_abordaje = SincronizacionAtencionLugarAbordaje(data=data.get('at_lugar_abordaje'))
        serializer_at_lugar_abordaje.is_valid(raise_exception=True)
        at_lugar_abordaje = serializer_at_lugar_abordaje.save()
        id_at_lugar_abordaje = at_lugar_abordaje.id

        data_paciente = data.get('paciente')

        try:
            paciente = Paciente.objects.get(
                numero_documento=data.get('paciente').get('numero_documento'),
                tipo_documento=data.get('paciente').get('tipo_documento'))
            ciudadano = CiudadanoClient(settings.MPI_API_TOKEN).ver(
                data.get('paciente').get('numero_documento'),
                data.get('paciente').get('tipo_documento'))
            data_paciente["paciente"] = ciudadano['uuid']
            serializer_paciente = SincronizacionPacienteSerializer(paciente, data_paciente)
            serializer_paciente.is_valid(raise_exception=True)

            if not data.get('examen'):
                return Response(serializer_paciente.data)
            else:
                data_atencion = {
                    'paciente': paciente.paciente,
                    'cita_uuid': None,
                    'fecha': data.get('examen').get('fecha_prueba'),
                    'ups': '1094',
                    'eess': data.get('examen').get('eess'),
                    'medico': data.get('examen').get('personal_salud'),
                    'tipo_registro': constants.TAMIZAJE_MOVIL,
                    'lugar_abordaje': id_at_lugar_abordaje
                }

                serializer_atencion = SincronizacionAtencionSerializer(data=data_atencion)
                serializer_atencion.is_valid(raise_exception=True)
                atencion = serializer_atencion.save()

                data_consejeria = {
                    'atencion': atencion.id,
                    'tipo_consejeria': constants.PRE,
                    'fecha_registro': data.get('examen').get('fecha_registro')
                }
                serializer_consejeria = SincronizacionConsejeriaSerializer(data=data_consejeria)
                serializer_consejeria.is_valid(raise_exception=True)
                consejeria = serializer_consejeria.save()
                if not data.get('examen').get('esta_consentido'):
                    return Response(serializer_paciente.data)
                else:
                    data_consejeria_pre = {
                        'consejeria': consejeria.id,
                        'tipo_poblacion': data.get('paciente').get('poblacion'),
                        'consejeria_previa': True,
                        'esta_consentido': data.get('examen').get('esta_consentido'),
                        'validacion': ''
                    }

                    serializer_consejeria_pre = SincronizacionConsejeriaPreSerializer(data=data_consejeria_pre)
                    serializer_consejeria_pre.is_valid(raise_exception=True)
                    serializer_consejeria_pre.save()

                    data_examen = data.get('examen')
                    data_examen['paciente'] = ciudadano['uuid']
                    data_examen['consejeria_pre'] = consejeria.id
                    serializer_examen = SincronizarExamenSerializer(data=data_examen)
                    serializer_examen.is_valid(raise_exception=True)
                    examen = serializer_examen.save()

                    if not data.get('examen').get('resultado_examen'):
                        return Response(serializer_paciente.data)
                    else:
                        data_examen_resultado = data.get('examen').get('resultado_examen')
                        data_examen_resultado["laboratorio_examen"] = examen.id

                        serializer_examen_resultado = ExamenResultadoSerializer(data=data_examen_resultado)
                        serializer_examen_resultado.is_valid(raise_exception=True)
                        serializer_examen_resultado.save()

                        return Response(serializer_paciente.data)
        except Paciente.DoesNotExist:

            try:

                ciudadano = CiudadanoClient(settings.MPI_API_TOKEN).ver(
                    data.get('paciente').get('numero_documento'),
                    data.get('paciente').get('tipo_documento'))
                data_paciente['paciente'] = ciudadano['uuid']

                serializer_paciente = SincronizacionPacienteSerializer(data=data_paciente)
                serializer_paciente.is_valid(raise_exception=True)
                paciente = serializer_paciente.save()

                if not data.get('examen'):
                    return Response(serializer_paciente.data)
                else:
                    data_atencion = {
                        'paciente': paciente.paciente,
                        'cita_uuid': None,
                        'fecha': data.get('examen').get('fecha_prueba'),
                        'ups': '1094',
                        'eess': data.get('examen').get('eess'),
                        'medico':  data.get('examen').get('personal_salud'),
                        'tipo_registro': constants.TAMIZAJE_MOVIL,
                        'lugar_abordaje': id_at_lugar_abordaje
                    }

                    serializer_atencion = SincronizacionAtencionSerializer(data=data_atencion)
                    serializer_atencion.is_valid(raise_exception=True)
                    atencion = serializer_atencion.save()

                    data_consejeria = {
                        'atencion': atencion.id,
                        'tipo_consejeria': constants.PRE,
                        'fecha_registro': data.get('examen').get('fecha_registro')
                    }
                    serializer_consejeria = SincronizacionConsejeriaSerializer(data=data_consejeria)
                    serializer_consejeria.is_valid(raise_exception=True)
                    consejeria = serializer_consejeria.save()
                    if not data.get('examen').get('esta_consentido'):
                        return Response(serializer_paciente.data)
                    else:
                        data_consejeria_pre = {
                            'consejeria': consejeria.id,
                            'tipo_poblacion': data.get('paciente').get('poblacion'),
                            'consejeria_previa': True,
                            'esta_consentido': data.get('examen').get('esta_consentido'),
                            'validacion': ''
                        }

                        serializer_consejeria_pre = SincronizacionConsejeriaPreSerializer(data=data_consejeria_pre)
                        serializer_consejeria_pre.is_valid(raise_exception=True)
                        serializer_consejeria_pre.save()

                        data_examen = data.get('examen')
                        data_examen['paciente'] = ciudadano['uuid']
                        data_examen['consejeria_pre'] = consejeria.id
                        serializer_examen = SincronizarExamenSerializer(data=data_examen)
                        serializer_examen.is_valid(raise_exception=True)
                        examen = serializer_examen.save()

                        data_examen_resultado = data.get('examen').get('resultado_examen')
                        data_examen_resultado["laboratorio_examen"] = examen.id

                        serializer_examen_resultado = ExamenResultadoSerializer(data=data_examen_resultado)
                        serializer_examen_resultado.is_valid(raise_exception=True)
                        serializer_examen_resultado.save()

                        return Response(serializer_paciente.data)
            except Exception as e:
                mpi_client = CiudadanoClient(settings.MPI_API_TOKEN)
                data_paciente_sin_documento = {
                    "nombres": data.get('paciente').get('nombres'),
                    "apellido_materno": data.get('paciente').get('apellido_materno'),
                    "apellido_paterno": data.get('paciente').get('apellido_paterno'),
                    "nombre_social": data.get('paciente').get('nombre_social'),
                    "sexo": data.get('paciente').get('sexo'),
                    "poblacion": data.get('paciente').get('poblacion'),
                    "correo": data.get('paciente').get('correo'),
                    "eess": data.get('paciente').get('eess'),
                    "etnia": data.get('paciente').get('etnia'),
                    "fecha_nacimiento": data.get('paciente').get('fecha_nacimiento'),
                    "telefono": data.get('paciente').get('telefono'),
                    'tipo_documento': constants.TIPO_SIN_DOCUMENTO,
                }
                datos_paciente_mpi = mpi_client.crear_sin_documento(data=data_paciente_sin_documento)
                if 'error' not in datos_paciente_mpi and 'errors' not in datos_paciente_mpi:
                    datos_paciente_mpi = datos_paciente_mpi.get('data').get('attributes')
                    data_paciente["paciente"] = datos_paciente_mpi.get('uuid', '')
                    data_paciente["numero_documento"] = datos_paciente_mpi.get('numero_documento', '')
                    data_paciente["tipo_documento"] = datos_paciente_mpi.get('tipo_documento', '')

                    paciente_serializer = PacientePoblacionSerializer(data=data_paciente)
                    if paciente_serializer.is_valid():
                        paciente_serializer.save()
                        if not data.get('examen'):
                            return Response(paciente_serializer.data)
                        else:
                            data_atencion = {
                                'paciente': datos_paciente_mpi.get('uuid', ''),
                                'cita_uuid': None,
                                'fecha': data.get('examen').get('fecha_prueba'),
                                'ups': '1094',
                                'eess': data.get('examen').get('eess'),
                                'medico': data.get('examen').get('personal_salud'),
                                'tipo_registro': constants.TAMIZAJE_MOVIL,
                                'lugar_abordaje': id_at_lugar_abordaje
                            }

                            serializer_atencion = SincronizacionAtencionSerializer(data=data_atencion)
                            serializer_atencion.is_valid(raise_exception=True)
                            atencion = serializer_atencion.save()

                            data_consejeria = {
                                'atencion': atencion.id,
                                'tipo_consejeria': constants.PRE,
                                'fecha_registro': data.get('examen').get('fecha_registro')
                            }
                            serializer_consejeria = SincronizacionConsejeriaSerializer(data=data_consejeria)
                            serializer_consejeria.is_valid(raise_exception=True)
                            consejeria = serializer_consejeria.save()
                            if not data.get('examen').get('esta_consentido'):
                                return Response(paciente_serializer.data)
                            else:
                                data_consejeria_pre = {
                                    'consejeria': consejeria.id,
                                    'tipo_poblacion': data.get('paciente').get('poblacion'),
                                    'consejeria_previa': True,
                                    'esta_consentido': data.get('examen').get('esta_consentido'),
                                    'validacion': ''
                                }

                                serializer_consejeria_pre = SincronizacionConsejeriaPreSerializer(
                                    data=data_consejeria_pre)
                                serializer_consejeria_pre.is_valid(raise_exception=True)
                                serializer_consejeria_pre.save()

                                data_examen = data.get('examen')
                                data_examen['paciente'] = datos_paciente_mpi.get('uuid', '')
                                data_examen['consejeria'] = consejeria.id
                                data_examen['consejeria_pre'] = consejeria.id

                                serializer_examen = SincronizarExamenSerializer(data=data_examen)
                                serializer_examen.is_valid(raise_exception=True)
                                examen = serializer_examen.save()

                                data_examen_resultado = data.get('examen').get('resultado_examen')
                                data_examen_resultado["laboratorio_examen"] = examen.id

                                serializer_examen_resultado = ExamenResultadoSerializer(data=data_examen_resultado)
                                serializer_examen_resultado.is_valid(raise_exception=True)
                                serializer_examen_resultado.save()

                                return Response(paciente_serializer.data)

                    return Response(paciente_serializer.errors, status=400)


class ObtenerEstablecimientosView(APIView):
    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):
        establecimientos = Establecimiento.objects.all()
        lista_establecimientos = []
        for establecimiento in establecimientos:
            data = {
                'diresa': establecimiento.diresa,
                'id': establecimiento.codigo_ipress,
                'categorizacion': establecimiento.categorizacion,
                'tipo': establecimiento.tipo,
                'condicion': establecimiento.condicion,
                'text': establecimiento.establecimiento_salud,
                'amp': establecimiento.amp,
                'pediatria': establecimiento.pediatria,
                'hepatitis_b': establecimiento.hepatitis_b,

            }
            lista_establecimientos.append(data)
        return Response(lista_establecimientos)


class BuscarEstablecimientoView(APIView):
    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):

        establecimientos = Establecimiento.objects.filter(
            Q(diresa__icontains=self.request.GET.get('nombre_establecimiento', '')) |
            Q(establecimiento_salud__icontains=self.request.GET.get('nombre_establecimiento', ''))).all()
        if establecimientos:
            lista_establecimiento = []

            for establecimiento in establecimientos:
                data = {
                    'id': establecimiento.codigo_ipress,
                    'text': establecimiento.establecimiento_salud
                }

                lista_establecimiento.append(data)

            return Response(lista_establecimiento)
        else:
            data = {"No existe establecimiento"}
            return Response(data, status.HTTP_204_NO_CONTENT)


class ObtenerEstablecimientosTotalesView(APIView):
    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):
        params = {'flag': 'TARV', 'dominio': settings.CATALOGO_ODOO_HOST_URL}
        headers = {'Authorization': 'Bearer {}'.format(settings.CATALOGO_ODOO_TOKEN), }
        url = "{dominio}/api/catalogominsa.renipress.eess?flag={flag}".format(**params)

        res = requests.get(url=url, headers=headers)

        lista_examenes = []
        if res.status_code == 200:
            data = res.json()['data']
            for examen in data:
                lista_examenes.append({
                    "id": examen["codigo_ipress"],
                    "text": examen["nombre"],
                    "diresa": examen["diresa_nombre"]
                })

        return Response(lista_examenes)


class BuscarEstablecimientosView(APIView):
    authentication_classes = (APITokenAuthentication,)

    def get(self, request, *args, **kwargs):

        params = {'flag': 'TARV', 'dominio': settings.CATALOGO_ODOO_HOST_URL}
        headers = {'Authorization': 'Bearer {}'.format(settings.CATALOGO_ODOO_TOKEN), }
        url = "{dominio}/api/catalogominsa.renipress.eess?flag={flag}".format(**params)

        res = requests.get(url=url, headers=headers)

        return Response(res)
