from django.db.models import Q

from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.common.views import APIProtectedView
from apps.medicamentos.models import Esquema, Medicamento

from .serializers import EsquemaSerializer, MedicamentoSerializer


class MedicamentoListAPIView(APIProtectedView, ListAPIView):
    serializer_class = MedicamentoSerializer
    queryset = Medicamento.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('$descripcion', )
    filter_fields = ('targa', )


class EsquemaListAPIView(APIProtectedView, ListAPIView):
    serializer_class = EsquemaSerializer
    queryset = Esquema.objects.all()


class EsquemaMedicamentoListAPIView(APIProtectedView, ListAPIView):
    serializer_class = MedicamentoSerializer

    def get_queryset(self):
        if self.request.GET.keys():
            get = self.request.GET.copy()
            if 'm1' and 'm2' and 'm3' in get:
                m1, m2, m3 = int(get.get('m1', 0)), int(get.get('m2', 0)), get.get('m3')
                esqs = Esquema.objects.values('medicamentos').filter(
                    Q(medicamentos__id=m1) | Q(medicamentos__id=m2)).filter(
                    medicamentos__descripcion__icontains=m3).distinct()
                return Medicamento.objects.filter(
                    pk__in=(m.get('medicamentos') for m in esqs if m.get('medicamentos') not in (m1, m2)))
            elif 'm1' and 'm2' in get:
                m1, m2 = int(get.get('m1', 0)), get.get('m2')
                esqs = Esquema.objects.values('medicamentos').filter(medicamentos__id=m1).filter(
                    medicamentos__descripcion__icontains=m2).distinct()
                return Medicamento.objects.filter(
                    pk__in=(m.get('medicamentos') for m in esqs if not m.get('medicamentos') == m1))
            if 'm1' in get:
                return Medicamento.objects.filter(pk__in=Esquema.objects.values('medicamentos').filter(
                    medicamentos__descripcion__icontains=self.request.GET.get('m1')))
        return Medicamento.objects.none()
