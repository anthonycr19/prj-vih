from rest_framework import serializers

from apps.laboratorio.models import Examen, ExamenResultado


class ExamenResultadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamenResultado
        fields = (
            'id', 'laboratorio_examen', 'resultado', 'nro_prueba', 'nro_muestra',
            'fecha_resultado', 'observacion', 'fecha_registro'
        )


class ExamenSerializer(serializers.ModelSerializer):
    estado_display = serializers.SerializerMethodField()
    cpt_data = serializers.SerializerMethodField()
    fecha = serializers.SerializerMethodField()
    resultados = ExamenResultadoSerializer(many=True, read_only=True)

    class Meta:
        model = Examen
        fields = ('id', 'estado_display', 'fecha', 'cpt_data', 'personal_salud', 'paciente', 'cpt', 'eess', 'estado',
                  'observaciones', 'consejeria_pre', 'fecha_prueba', 'resultados')
        read_only_fields = ('estado_display', 'cpt_data', 'fecha')

    def get_estado_display(self, obj):
        return obj.get_estado_display()

    def get_fecha(self, obj):
        if obj.fecha_prueba:
            return obj.fecha_prueba.strftime('%d/%m/%Y')
        return ''

    def get_cpt_data(self, obj):
        return obj.cpt_data


class ExamenResultadoSerializer(serializers.ModelSerializer):
    laboratorio_examen = ExamenSerializer()
    observaciones = serializers.SerializerMethodField()
    fecha = serializers.SerializerMethodField()

    class Meta:
        model = ExamenResultado
        fields = ('id', 'laboratorio_examen', 'resultado', 'nro_prueba', 'nro_muestra',
                  'fecha_resultado', 'observacion', 'fecha', 'observaciones')
        read_only_fields = ('observaciones', 'fecha')

    def get_observaciones(self, obj):
        if obj.laboratorio_examen.estado == '2':
            return obj.observacion
        return obj.laboratorio_examen.observaciones

    def get_fecha(self, obj):
        if obj.fecha_resultado:
            return obj.fecha_resultado.strftime('%d/%m/%Y')
        return ''


class CreateExamenResultadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenResultado
        fields = (
            'id', 'laboratorio_examen', 'resultado', 'nro_prueba', 'nro_muestra', 'fecha_resultado', 'observacion',
            'post_test',
            'ficha_informativa', 'refiere_eess', 'codigo_eess', 'nombre_eess', 'fecha_cita', 'fecha_registro',
            'repite_prueba', 'cantidad_condones', 'cantidad_lubricantes'
        )
