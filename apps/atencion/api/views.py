from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_json_api.renderers import JSONRenderer as JSONAPIRenderer

from apps.afiliacion.models import Paciente
from apps.atencion.models import Atencion, AtencionDiagnostico, AtencionTratamiento
from apps.common.functions import consulta_servicio_ciudadano_uuid
from .serializers import AtencionDiagnosticoSerializer, AtencionSerializer, AtencionTratamientoSerializer, \
    DatosPacienteSerializer, PacienteSerializer


class PacienteDataAPIView(generics.RetrieveAPIView):
    serializer_class = PacienteSerializer
    model = Paciente
    queryset = Paciente.objects.all()


class PacienteBuscarNombresApellidosAPIView(generics.ListAPIView):
    serializer_class = DatosPacienteSerializer
    renderer_classes = (JSONAPIRenderer, BrowsableAPIRenderer)

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q:
            terms = q.split(" ")
            search = [(Q(nombres__icontains=word) | Q(apellido_paterno__icontains=word) | Q(apellido_materno__icontains=word)) for word in terms]  # noqa
            return Paciente.objects.filter(*search)
        else:
            raise Http404


class PacienteVerUUIDDataAPIView(generics.RetrieveAPIView):
    serializer_class = DatosPacienteSerializer
    renderer_classes = (JSONAPIRenderer, BrowsableAPIRenderer)
    queryset = []

    def get_object(self):
        uuid = self.kwargs['uuid']
        datos_paciente = Paciente.objects.filter(paciente=uuid)
        if datos_paciente:
            return Paciente.objects.get(paciente=uuid)
        else:
            datos_mpi = consulta_servicio_ciudadano_uuid(uuid)
            if datos_mpi['resultado'] == 'OK':
                return Paciente.objects.get(paciente=datos_mpi['uuid'])
            else:
                raise NotFound


class AtencionDataAPIView(generics.RetrieveAPIView):
    serializer_class = AtencionSerializer
    model = Atencion
    queryset = Atencion.objects.all()


class AtencionDiagnosticoDataAPIView(generics.RetrieveAPIView):
    serializer_class = AtencionDiagnosticoSerializer
    model = AtencionDiagnostico
    queryset = AtencionDiagnostico.objects.all()

    def get_object(self):
        if self.kwargs.get('id'):
            self.object = get_object_or_404(
                self.get_queryset(),
                atencion=self.kwargs.get('atencion'),
                id=self.kwargs.get('id'))
        else:
            self.object = get_object_or_404(
                self.get_queryset(),
                atencion=self.kwargs.get('atencion'),
                tipo_diags='P')
        return self.object


class AtencionDispensacionListAPIView(generics.ListAPIView):
    # serializer_class = DispensacionSerializer
    # model = Dispensacion

    def get_queryset(self):
        if not self.queryset:
            self.queryset = get_list_or_404(
                self.model,
                tratamiento__atencion=self.kwargs.get('pk'),
                tratamiento__medicamento__targa=True)
        return self.queryset


class AtencionTratamientoListAPIView(generics.ListAPIView):
    serializer_class = AtencionTratamientoSerializer

    def get_queryset(self):
        return AtencionTratamiento.objects.filter(atencion=self.kwargs.get('pk'))
