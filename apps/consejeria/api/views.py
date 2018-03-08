from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import generics
from apps.common.views import EnfermeriaProtectedView
from apps.consejeria.models import ConsejeriaPre, ConsejeriaPost
from apps.atencion.api.serializers import AtencionSerializer

from .serializers import ConsejeriaSerializer, ConsejeriaPreSerializer, ConsejeriaPostSerializer


class CreateConsejeriaPreAPIView(EnfermeriaProtectedView, generics.ListCreateAPIView):
    serializer_class = ConsejeriaPreSerializer
    model = ConsejeriaPre
    queryset = ConsejeriaPre.objects.all()
    filter_fields = ('consejeria__atencion__paciente', 'tipo_poblacion', 'consejeria_previa')

    def post(self, request, *args, **kwargs):
        try:
            atencion = AtencionSerializer.get_atencion(request.POST)
            consejeria_serializer = ConsejeriaSerializer(data=request.POST)
            pre_serializer = ConsejeriaPreSerializer(data=request.POST)
            if not consejeria_serializer.is_valid():
                return JsonResponse(consejeria_serializer.errors, status=400)
            if not pre_serializer.is_valid():
                return JsonResponse(pre_serializer.errors, status=400)

            consejeria_serializer.save(atencion=atencion)
            pre_serializer.save(consejeria=consejeria_serializer.instance)
            lista_data = []
            paciente = request.POST['paciente']
            pre_consejeria = ConsejeriaPre.objects.filter(consejeria__atencion__paciente__paciente=paciente)
            for obj in pre_consejeria:
                lista_data.append({
                    'nombre_completo': obj.consejeria.atencion.paciente.nombre_completo,

                    'fecha_consejeria': obj.consejeria.fecha_registro.strftime("%Y-%m-%d"),
                    'consejeria_previa': obj.consejeria_previa,
                })
            return JsonResponse({'data': lista_data}, status=200)
        except IntegrityError:
            return JsonResponse({'Mensaje': 'Consejeria Previa ya registrada anteriormente.'}, status=400)


class DataConsejeriaPreAPIView(EnfermeriaProtectedView, generics.RetrieveUpdateAPIView):
    serializer_class = ConsejeriaPreSerializer
    queryset = ConsejeriaPre.objects.all()
    lookup_field = 'pk'


class ConsejeriaPostListAPIView(EnfermeriaProtectedView, generics.ListAPIView):
    model = ConsejeriaPost
    serializer_class = ConsejeriaPostSerializer
    queryset = ConsejeriaPost.objects.all()
    filter_fields = ('via_transmision', 'consejeria__atencion__paciente')
