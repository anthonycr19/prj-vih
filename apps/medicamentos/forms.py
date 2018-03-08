from django import forms

from .models import Medicamento


class AjaxMedicamentoForm(forms.ModelForm):

    class Meta:
        model = Medicamento
        fields = ('abreviatura', 'descripcion')

    def __init__(self, *args, **kwargs):
        super(AjaxMedicamentoForm, self).__init__(*args, **kwargs)
        self.fields['abreviatura'].required = True
        self.fields['descripcion'].required = True
