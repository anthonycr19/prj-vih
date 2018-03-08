from django import forms
from django.forms import inlineformset_factory

from apps.afiliacion.models import Paciente
from apps.common import constants

from .models import (Atencion, AtencionDescarteCoinfeccion,
                     AtencionDiagnostico, AtencionExamenAuxiliar,
                     AtencionExamenFisico, AtencionGestacion, AtencionRam,
                     AtencionTerapia, AtencionTratamiento, ExamenFisico,
                     Triaje, Egreso)


class AtencionForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(queryset=Paciente.objects.all(), required=True, widget=forms.HiddenInput())
    eess = forms.CharField(required=True, widget=forms.HiddenInput())
    medico = forms.CharField(required=True, widget=forms.HiddenInput())
    cita = forms.CharField(required=False, widget=forms.HiddenInput())
    ups = forms.CharField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = Atencion
        fields = ('cita', 'paciente', 'medico', 'eess', 'ups')


class TriajeForm(forms.ModelForm):
    anamnesis = forms.CharField(label="Anamnesis", help_text="", widget=forms.Textarea(
        attrs={'rows': 3, 'placeholders': 'Describa ...', 'maxlength': '500'}))

    class Meta:
        model = Triaje
        fields = ('anamnesis', 'peso', 'talla', 'temperatura', 'imc', 'frecuencia_cardiaca', 'frecuencia_respiratoria',
                  'atencion')
        widgets = {
            'atencion': forms.HiddenInput(),
        }


class AtencionExamenFisicoForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    estado = forms.TypedChoiceField(choices=constants.ESTADO_EXAMEN_FISICO_CHOICES, widget=forms.RadioSelect,
                                    initial='0')

    class Meta:
        model = AtencionExamenFisico
        fields = ('examen_fisico', 'estado', 'obs', 'id')
        widgets = {
            'examen_fisico': forms.HiddenInput(),
        }


ExamenFisicoFormSet = inlineformset_factory(Atencion, AtencionExamenFisico, form=AtencionExamenFisicoForm, extra=0,
                                            min_num=ExamenFisico.size())


class AtencionDiagnosticoForm(forms.ModelForm):
    descie = forms.CharField(label='Buscar CIEX', widget=forms.TextInput(attrs={'placeholder': 'Digite un CIE', }))
    tipo_dx = forms.ChoiceField(label='Tipo de Diagnóstico', widget=forms.RadioSelect(),
                                choices=constants.TIPO_DIAGNOSTICO_CHOICES, initial='P')

    class Meta:
        model = AtencionDiagnostico
        fields = ('atencion', 'estadio', 'tipo_dx', 'indicacion', 'cie')
        widgets = {
            'cie': forms.HiddenInput(),
            'indicacion': forms.Textarea(attrs={'rows': 3}),
            'atencion': forms.HiddenInput(),
        }


class AtencionTratamientoForm(forms.ModelForm):
    nro_dias = forms.IntegerField(min_value=1, initial=1, label='N° de dias')
    cantidad_dia = forms.IntegerField(min_value=1, initial=1, label='N° a suministrar por dia')

    class Meta:
        model = AtencionTratamiento
        fields = ('medicamento', 'cantidad_dia', 'nro_dias', 'indicacion')
        widgets = {
            'medicamento': forms.HiddenInput(),
        }


AtencionTratamientoFormSet = inlineformset_factory(Atencion, AtencionTratamiento, form=AtencionTratamientoForm, extra=3,
                                                   min_num=3, max_num=6)


class AtencionGestacionForm(forms.ModelForm):
    fur = forms.DateField(required=True, label='FUR', input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])
    fpp = forms.DateField(required=True, label='FPP', input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])
    edad = forms.IntegerField(required=True, label='Edad', min_value=1, max_value=9, initial=1)

    class Meta:
        model = AtencionGestacion
        fields = ('atencion', 'fur', 'fpp', 'edad')
        widgets = {
            'atencion': forms.HiddenInput(),
        }


class AtencionTerapiaForm(forms.ModelForm):
    tuvo_terapia = forms.TypedChoiceField(choices=constants.BOOLEAN_CHOICES, widget=forms.RadioSelect, initial=True,
                                          label='¿Tuvo terapia preventiva?')
    terapia = forms.IntegerField(initial=constants.RIFAPENTINA_ISONIACIDA, label='Terapia Preventiva', required=True,
                                 widget=forms.Select(choices=constants.TERAPIA_PREVENTIVA))
    fecha_inicio = forms.DateField(required=False, label='Fecha de Inicio',
                                   input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])
    fecha_fin = forms.DateField(required=False, label='Fecha de Fin',
                                input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])

    class Meta:
        model = AtencionTerapia
        fields = ('atencion', 'tuvo_terapia', 'terapia', 'fecha_inicio', 'fecha_fin', 'razon')
        widgets = {
            'atencion': forms.HiddenInput(),
            'razon': forms.Textarea(attrs={'rows': 2}),
        }


class AtencionRamForm(forms.ModelForm):
    fg_presenta_ram = forms.TypedChoiceField(choices=constants.BOOLEAN_CHOICES, widget=forms.RadioSelect, initial=False,
                                             label='¿Presenta RAM?')
    fecha_inicio = forms.DateField(required=False, label='Fecha de Inicio',
                                   input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])
    fecha_fin = forms.DateField(required=False, label='Fecha de Fin',
                                input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])

    class Meta:
        model = AtencionRam
        fields = ('atencion', 'ram', 'descripcion', 'fg_presenta_ram', 'fecha_inicio', 'fecha_fin', 'fg_gravedad',
                  'descripcion_gravedad')
        widgets = {
            'atencion': forms.HiddenInput(),
            'descripcion_gravedad': forms.Textarea(attrs={'rows': 2}),
            'ram': forms.Select(choices=())
        }

    def clean_ram(self):
        ram = self.cleaned_data.get("ram")
        atencion = self.cleaned_data.get("atencion")
        if AtencionRam.objects.filter(atencion__paciente=atencion.paciente, ram=ram).exists():
            msg = 'Estimado usuario, ya existe en el listado el Medicamento: {}.'.format(ram.descripcion)
            raise forms.ValidationError(msg)
        return ram


class DescarteCoinfeccionForm(forms.ModelForm):
    tiene_descarte = forms.TypedChoiceField(choices=constants.BOOLEAN_CHOICES, widget=forms.RadioSelect, initial=False)
    fecha_descarte = forms.DateField(required=False, label='Fecha Descarte',
                                     input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])
    cie = forms.CharField(max_length=50, label='Buscar', widget=forms.Select())

    class Meta:
        model = AtencionDescarteCoinfeccion
        fields = ('cie', 'observacion', 'fecha_descarte', 'tiene_descarte', 'infeccion')
        widgets = {
            'infeccion': forms.HiddenInput(),
        }

    def clean_tiene_descarte(self):
        tiene_descarte = self.cleaned_data.get("tiene_descarte")
        if tiene_descarte:
            return tiene_descarte
        raise forms.ValidationError('No tiene descarte')


DescarteCoinfeccionFormSet = inlineformset_factory(Atencion, AtencionDescarteCoinfeccion, form=DescarteCoinfeccionForm,
                                                   max_num=3, extra=3)


class ExamenAuxForm(forms.ModelForm):
    imagen_fecha = forms.DateField(required=False, label='Fecha de Fin',
                                   input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])
    laboratorio_fecha = forms.DateField(required=False, label='Fecha de Fin',
                                        input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])
    procedimiento_fecha = forms.DateField(required=False, label='Fecha de Fin',
                                          input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])

    def clean(self):
        cleaned_data = super(ExamenAuxForm, self).clean()
        imagen = cleaned_data.get("imagen", False)
        laboratorio = cleaned_data.get("laboratorio", False)
        procedimiento = cleaned_data.get("procedimiento", False)
        atencion = cleaned_data.get("atencion")
        if not laboratorio and not procedimiento and not imagen:
            raise forms.ValidationError('Debe seleccionar por lo menos un examen auxiliar.')
        exams = AtencionExamenAuxiliar.objects.filter(atencion__paciente=atencion.paciente)
        msg = 'Estimado usuario, ya existe en el listado el examen: {}.'
        if exams.filter(imagen=imagen).exists():
            raise forms.ValidationError(msg.format(imagen))
        if exams.filter(laboratorio=laboratorio).exists():
            raise forms.ValidationError(msg.format(laboratorio))
        if exams.filter(procedimiento=procedimiento).exists():
            raise forms.ValidationError(msg.format(procedimiento))

    class Meta:
        model = AtencionExamenAuxiliar
        fields = ('atencion', 'imagen', 'imagen_fecha', 'laboratorio', 'laboratorio_fecha', 'procedimiento',
                  'procedimiento_fecha')
        widgets = {
            'atencion': forms.HiddenInput(),
            'imagen': forms.Select(),
            'laboratorio': forms.Select(),
            'procedimiento': forms.Select(),
        }


class EgresoForm(forms.ModelForm):
    class Meta:
        model = Egreso
        fields = ('tipo_egreso', 'numero_episodio', 'lugar_fallecimiento', 'fecha_egreso', 'causa_fallecimiento')
