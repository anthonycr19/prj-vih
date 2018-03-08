from django import forms

from apps.common import constants
from apps.common.constants import Antecendentes
from .models import Consejeria, ConsejeriaPost


class ConsejeriaForm(forms.ModelForm):
    class Meta:
        model = Consejeria
        fields = ['atencion', 'tipo_consejeria']


class ConsejeriPostForm(forms.ModelForm):
    via_transmision = forms.CharField(
        label='Vía de Transmisición',
        max_length=100,
        widget=forms.Select(choices=constants.VIA_TRANSMISION, attrs={'v-model': 'via_transmision'}))
    antecedentes = forms.CharField(label='Antecedentes', max_length=100,
                                   widget=forms.Select(choices=Antecendentes.to_choice()))
    tipo_transmision = forms.CharField(label='Tipo de Transmisión', max_length=100, required=False)
    nro_parejas = forms.IntegerField(label='N° de parejas', min_value=1, initial=1)
    uso_preservativo = forms.BooleanField(
        initial=False,
        label='¿Uso preservativo en la última relación sexual?',
        required=False
    )

    class Meta:
        model = ConsejeriaPost
        fields = ['via_transmision', 'antecedentes', 'tipo_transmision', 'nro_parejas', 'uso_preservativo']
