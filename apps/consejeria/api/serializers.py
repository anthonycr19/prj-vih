from apps.atencion.api.serializers import AtencionSerializer
from apps.consejeria.models import Consejeria, ConsejeriaPost, ConsejeriaPre
from rest_framework import serializers


class ConsejeriaSerializer(serializers.ModelSerializer):
    atencion = AtencionSerializer(read_only=True)

    class Meta:
        model = Consejeria
        fields = ('tipo_consejeria', 'fecha_registro', 'atencion')
        read_only_fields = ('fecha_registro', 'atencion_detalle')


class ConsejeriaPreSerializer(serializers.ModelSerializer):
    consejeria = ConsejeriaSerializer(read_only=True)
    fecha_atencion = serializers.SerializerMethodField()
    poblacion = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = ConsejeriaPre
        fields = (
            'consejeria', 'tipo_poblacion', 'consejeria_previa', 'esta_consentido',
            'validacion', 'fecha_atencion', 'poblacion'
        )
        read_only_fields = ('fecha_registro', 'consejeria', 'poblacion')

    def get_fecha_atencion(self, obj):
        return obj.consejeria.fecha_registro.strftime('%Y-%m-%d')

    def get_poblacion(self, obj):
        return obj.tipo_poblacion.denominacion


class ConsejeriaPostSerializer(serializers.ModelSerializer):
    consejeria = ConsejeriaSerializer(read_only=True)
    fecha_atencion = serializers.SerializerMethodField(read_only=True)
    antecedentes_display = serializers.SerializerMethodField(read_only=True)
    tipo_transmision_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ConsejeriaPost
        fields = ['id', 'consejeria',  'fecha_atencion', 'antecedentes_display',
                  'tipo_transmision_display', 'nro_parejas', 'uso_preservativo']

    def get_fecha_atencion(self, obj):
        return obj.consejeria.fecha_registro.strftime('%Y-%m-%d')

    def get_antecedentes_display(self, obj):
        return obj.get_antecedentes_display()

    def get_tipo_transmision_display(self, obj):
        return obj.get_tipo_transmision_display()
