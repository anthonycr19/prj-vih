from rest_framework import serializers

from apps.medicamentos.models import Medicamento, Esquema


class MedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicamento
        fields = ['id', 'descripcion', 'presentacion', 'concentracion', 'targa']


class EsquemaSerializer(serializers.ModelSerializer):
    medicamentos = MedicamentoSerializer(many=True)

    class Meta:
        model = Esquema
        fields = ['id', 'descripcion', 'tipo', 'etapa_crecimiento', 'n_meses', 'medicamentos']
