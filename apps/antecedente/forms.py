from django import forms
from django.forms import modelformset_factory
from django.utils import timezone

from .models import (AntecedenteFamiliar, AntecedentePersonal,
                     AntecedenteTerapiaAntirretroviral,
                     AntecedenteTerapiaPreventiva, AntecedenteVacunaRecibida)


class AntecedentePersonalForm(forms.ModelForm):
    obs = forms.CharField(widget=forms.TextInput(), required=False)
    cie = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=True)
    fecha_dx = forms.DateField(input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])

    class Meta:
        model = AntecedentePersonal
        fields = ('tipo_enfermedad', 'fecha_dx', 'obs', 'cie')


class AntecedenteFamiliarForm(forms.ModelForm):
    obs = forms.CharField(widget=forms.TextInput(), required=False)
    cie = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    fecha_dx = forms.DateField(input_formats=['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'])

    class Meta:
        model = AntecedenteFamiliar
        fields = ('parentesco', 'fecha_dx', 'obs', 'cie')


class AntecedenteTerapiaAntirretroviralForm(forms.ModelForm):
    med1 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Digite medicamento 1', }))
    med2 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Digite medicamento 2', }))
    med3 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Digite medicamento 3', }))
    med4 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Digite medicamento 4', }))
    med5 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Digite medicamento 5', }))

    class Meta:
        model = AntecedenteTerapiaAntirretroviral
        fields = (
            'medicamento1', 'medicamento2', 'medicamento3', 'medicamento4', 'medicamento5', 'fecha_inicio', 'fecha_fin',
            'obs', 'med1', 'med2', 'med3', 'med4', 'med5', 'atencion')
        widgets = {
            'medicamento1': forms.HiddenInput(),
            'medicamento2': forms.HiddenInput(),
            'medicamento3': forms.HiddenInput(),
            'medicamento4': forms.HiddenInput(),
            'medicamento5': forms.HiddenInput(),
            'atencion': forms.HiddenInput(),
            'obs': forms.Textarea(),
        }

    def clean(self):
        cleaned_data = super(AntecedenteTerapiaAntirretroviralForm, self).clean()
        med1 = cleaned_data.get("med1")
        if not med1:
            self.add_error('med1', 'Ingrese un medicamento')

        med2 = cleaned_data.get("med2")
        if not med2:
            self.add_error('med2', 'Ingrese un medicamento')

        med3 = cleaned_data.get("med3")
        if not med3:
            self.add_error('med3', 'Ingrese un medicamento')

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_hoy = timezone.now().date()

        if not fecha_inicio <= fecha_hoy:
            self.add_error('fecha_inicio', 'Ingrese una fecha menor a la actual')

        fecha_fin = cleaned_data.get('fecha_fin')
        if not fecha_fin <= fecha_hoy:
            self.add_error('fecha_fin', 'Ingrese una fecha menor a la actual')

        if not fecha_inicio < fecha_fin:
            self.add_error('fecha_fin', 'Ingrese un intervalo de fecha valido')
            self.add_error('fecha_inicio', 'Ingrese un intervalo de fecha valido')

        return cleaned_data


class AntecedenteTerapiaPreventivaForm(forms.ModelForm):
    fecha_inicio_tub = forms.DateField(required=False)

    class Meta:
        model = AntecedenteTerapiaPreventiva
        fields = ('atencion', 'tiene_terapia_tub', 'razon_cambio_tub', 'fecha_inicio_tub', 'tiene_terapia_pne',
                  'razon_cambio_pne', 'fecha_inicio_pne')
        widgets = {
            'atencion': forms.HiddenInput(),
        }


class AntecedenteVacunaRecibidaForm(forms.ModelForm):
    class Meta:
        model = AntecedenteVacunaRecibida
        fields = ('atencion', 'vacuna', 'nro_dosis', 'fecha_aplicacion')
        widgets = {
            'atencion': forms.HiddenInput(),
        }


AntecedentePersonalFormSet = modelformset_factory(AntecedentePersonal, form=AntecedentePersonalForm, min_num=4)

AntecedentesFamiliariesFormSet = modelformset_factory(AntecedenteFamiliar, form=AntecedenteFamiliarForm, min_num=4)
