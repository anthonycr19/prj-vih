from django.shortcuts import redirect
from django.urls import reverse

from rest_framework import generics

from apps.common.views import EnfermeriaProtectedView
from apps.laboratorio.models import Examen, ExamenResultado

from .serializers import CreateExamenResultadoSerializer, ExamenSerializer, ExamenResultadoSerializer


class ExamenListCreateAPIView(EnfermeriaProtectedView, generics.ListCreateAPIView):
    serializer_class = ExamenSerializer
    model = Examen
    queryset = Examen.objects.all()
    filter_fields = ('consejeria_pre', 'paciente')

    def post(self, request, *args, **kwargs):
        examen_serializer_ = ExamenSerializer(data=request.POST)
        examen_serializer_.is_valid(raise_exception=True)
        examen_serializer_.save()
        return redirect(reverse('laboratorio:v1:examen', args=(examen_serializer_.instance.pk, )))


class ExamenResultadoDataAPIView(EnfermeriaProtectedView, generics.RetrieveUpdateAPIView):
    serializer_class = ExamenResultadoSerializer
    queryset = ExamenResultado.objects.all()
    lookup_field = 'pk'


class DataExamenAPIView(EnfermeriaProtectedView, generics.RetrieveUpdateAPIView):
    serializer_class = ExamenSerializer
    queryset = Examen.objects.all()
    lookup_field = 'pk'


class ExamenResultadoListAPIView(EnfermeriaProtectedView, generics.ListAPIView):
    serializer_class = ExamenResultadoSerializer
    model = ExamenResultado
    queryset = ExamenResultado.objects.all()
    filter_fields = ('laboratorio_examen__paciente', 'laboratorio_examen', 'nro_muestra', 'resultado')


class CreateExamenResultadoListAPIView(EnfermeriaProtectedView, generics.CreateAPIView):
    serializer_class = CreateExamenResultadoSerializer


class EditarExamenResultadoUpdateAPIView(EnfermeriaProtectedView, generics.RetrieveUpdateAPIView):
    http_method_names = ['put', ]
    serializer_class = CreateExamenResultadoSerializer
    queryset = ExamenResultado.objects.all()
    lookup_field = 'pk'
