# coding: utf-8
from __future__ import unicode_literals
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext as _

from .models import User

MEDICINA_GENERAL = 'medicina_general'
INFECTOLOGIA = 'infectologia'
CONSEJERIA = 'consejeria'
ENFERMERIA = 'enfermeria'
LABORATORIO = 'laboratorio'
PSICOLOGIA = 'psicologia'
GINECOLOGIA = 'ginecologia'
ASISTENCIA_SOCIAL = 'asistencia_social'
TOPICO_DE_URGENCIAS = 'topico_de_urgencias'
CHOICES_SERVICIOS = (
    (MEDICINA_GENERAL, 'Medicina General'),
    (INFECTOLOGIA, 'Infectología'),
    (CONSEJERIA, 'Consejería'),
    (ENFERMERIA, 'Enfermería'),
    (LABORATORIO, 'Laboratorio'),
    (PSICOLOGIA, 'Psicología'),
    (GINECOLOGIA, 'Ginecología'),
    (ASISTENCIA_SOCIAL, 'Asistencia Social'),
    (TOPICO_DE_URGENCIAS, 'Tópico de Urgencias'),
)


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    numero_colegiatura = forms.CharField(label='Número de Colegiatura', max_length=100, required=False)
    dni = forms.IntegerField(label='DNI', required=False)
    celular = forms.IntegerField(label='Celular', required=False)
    es_paciente = forms.BooleanField(label='Es paciente', required=False)

    class Meta:
        model = User
        fields = ('email', 'servicio', 'numero_colegiatura', 'dni', 'celular', 'username', 'first_name', 'last_name',
                  'es_paciente', 'eess')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))
    numero_colegiatura = forms.CharField(label='Número de Colegiatura', max_length=100, required=False)
    dni = forms.IntegerField(label='DNI', required=False)
    celular = forms.IntegerField(label='Celular', required=False)
    email = forms.EmailField(label='Correo', required=False)
    es_paciente = forms.BooleanField(label='Es paciente', required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_active', 'is_admin', 'servicio', 'numero_colegiatura', 'dni',
                  'celular', 'first_name', 'last_name', 'es_paciente')

    def clean_password(self):
        return self.initial['password']


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(label=_('New password'), widget=forms.PasswordInput, required=True)
    repeat_new_password = forms.CharField(label=_('Repeat new password'), widget=forms.PasswordInput, required=True)

    def clean_repeat_new_password(self):
        new_password = self.cleaned_data.get('new_password', '')
        repeat_new_password = self.cleaned_data.get('repeat_new_password', '')
        if new_password and repeat_new_password and new_password != repeat_new_password:
            raise forms.ValidationError(_('Password must be equal'))
        return repeat_new_password
