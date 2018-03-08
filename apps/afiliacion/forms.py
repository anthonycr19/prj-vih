import logging

from django import forms
from django.conf import settings
from django.utils import timezone
from mpi_client.client import MPIClient

from apps.common import constants
from .models import Brigada, HCE, Paciente, PacienteContactoFamiliar

logger = logging.getLogger(__name__)


class BrigadistaForm(forms.ModelForm):

    departamento = forms.ChoiceField(label='Departamento', required=False, widget=forms.Select())
    provincia = forms.ChoiceField(label='Provincia', required=False, widget=forms.Select())
    distrito = forms.ChoiceField(label='Distrito', required=False, widget=forms.Select())
    departamento_nombre = forms.CharField(widget=forms.HiddenInput, required=False)
    provincia_nombre = forms.CharField(widget=forms.HiddenInput, required=False)
    distrito_nombre = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Brigada
        fields = (
            'nombre', 'ubigeo_departamento', 'ubigeo_provincia', 'ubigeo_distrito',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nacimiento_pais'] = forms.ChoiceField(
            label='Pais',
            choices=[('', '---------')] +
            self.get_paises(), initial=constants.ID_PAIS_PERU, required=False)

        self.fields['departamento'] = forms.ChoiceField(
            label='Departamento',
            choices=[('', '---------')] + self.get_departamentos(), initial=None, required=False)

        self.fields['provincia'] = forms.ChoiceField(
            label='Provincia',
            choices=[('', '---------')] + self.get_provincias(self['departamento'].value()), initial=None,
            required=False)

        self.fields['distrito'] = forms.ChoiceField(
            label='Distrito',
            choices=[('', '---------')] + self.get_distritos(
                        self['departamento'].value(),
                        self['provincia'].value()), initial=None, required=False)

    def get_paises(self):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/?page_size=100'.format(settings.MPI_API_HOST)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_pais'], obj['attributes']['ubigeo_pais'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_departamentos(self):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/?page_size=100'.format(settings.MPI_API_HOST)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_departamento'], obj['attributes']['ubigeo_departamento'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_provincias(self, dep_id):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            response = client.get(
                '{}/api/v1/ubigeo/1/177/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id),
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append((
                        obj['attributes']['cod_ubigeo_inei_provincia'],
                        obj['attributes']['ubigeo_provincia']
                    ))
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_distritos(self, dep_id, prov_id):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/{}/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id, prov_id)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_distrito'], obj['attributes']['ubigeo_distrito'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data


class LugarAbordajePorPaciente(forms.ModelForm):
    nombre = forms.CharField(label='')
    detalle = forms.CharField(label='Otros')
    fecha = forms.DateField(label='Fecha de Abordaje')


class PacienteSinDniForm(forms.ModelForm):
    tipo_documento = forms.ChoiceField(
        label='Tipo de Documento',
        required=True,
        choices=(('', '-----------------'),) + constants.TDOC_CHOICES
    )
    numero_documento = forms.CharField(label='Número de Documento', required=False)
    nombres = forms.CharField(label='Nombres', required=True)
    apellido_paterno = forms.CharField(label='Apellido Paterno', required=False)
    apellido_materno = forms.CharField(label='Apellido Materno', required=True)
    fecha_nacimiento = forms.DateField(label='Fecha Nacimiento', required=True)
    sexo = forms.ChoiceField(
        label='Sexo',
        required=True,
        choices=(('', '-----------------'),) + constants.SEXO_CHOICES
    )
    estado_civil = forms.ChoiceField(
        label='Estado Civil',
        required=False,
        choices=(('', '-----------------'),) + constants.EC_CHOICES
    )
    etnia = forms.ChoiceField(
        label='Etnia',
        required=False,
        choices=(('', '-----------------'),) + constants.ETNIA_CHOICES
    )

    nacimiento_pais = forms.CharField(label='País', required=False, widget=forms.Select())
    nacimiento_departamento = forms.ChoiceField(label='Departamento', required=False, widget=forms.Select())
    nacimiento_provincia = forms.CharField(label='Provincia', required=False, widget=forms.Select(choices=[]))
    nacimiento_distrito = forms.CharField(label='Distrito', required=False, widget=forms.Select(choices=[]))
    residencia_departamento = forms.CharField(label='Departamento', required=False, widget=forms.Select())
    residencia_provincia = forms.CharField(label='Provincia', required=False, widget=forms.Select(choices=[]))
    residencia_distrito = forms.CharField(label='Distrito', required=False, widget=forms.Select(choices=[]))
    residencia_actual_pais = forms.CharField(label='País', required=False, widget=forms.Select())
    residencia_actual_departamento = forms.ChoiceField(label='Departamento', required=False, widget=forms.Select())
    residencia_actual_provincia = forms.CharField(label='Provincia', required=False, widget=forms.Select(choices=[]))
    residencia_actual_distrito = forms.CharField(label='Distrito', required=False, widget=forms.Select(choices=[]))
    centro_poblado_actual = forms.CharField(label='Localidad', required=False, widget=forms.Select(choices=[]))
    direccion_actual = forms.CharField(label='Dirección Actual', required=False)
    referencia_actual = forms.CharField(label='Referencia Actual', required=False)
    grado_instruccion = forms.ChoiceField(
        label='Grado de Instrucción',
        required=False,
        choices=(('', '-----------------'),) + constants.GI_CHOICES
    )
    ocupacion = forms.ChoiceField(
        label='Ocupación',
        required=False,
        choices=(('', '-----------------'),) + constants.OCUPACION_CHOICES
    )
    telefono = forms.CharField(label='Teléfono', required=False)
    celular = forms.CharField(label='Celular', required=False)
    correo = forms.CharField(label='Correo electrónico', required=False)
    latitud = forms.CharField(label='Correo electrónico', required=False)
    longitud = forms.CharField(label='Correo electrónico', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nacimiento_pais'] = forms.ChoiceField(
            label='Pais',
            choices=[('', '---------')] +
            self.get_paises(), initial=constants.ID_PAIS_PERU, required=False)

        self.fields['residencia_actual_pais'] = forms.ChoiceField(
            label='Pais',
            choices=[('', '---------')] +
            self.get_paises(), initial=constants.ID_PAIS_PERU, required=False)

        self.fields['nacimiento_departamento'] = forms.ChoiceField(
            label='Departamento',
            choices=[('', '---------')] +
            self.get_departamentos(), initial=None, required=False)

        self.fields['nacimiento_provincia'] = forms.ChoiceField(
            label='Provincias',
            choices=[('', '---------')] +
            self.get_provincias(self['nacimiento_departamento'].value()), initial=None, required=False)

        self.fields['nacimiento_distrito'] = forms.ChoiceField(
            label='Distrito',
            choices=[('', '---------')] +
            self.get_distritos(
                self['nacimiento_departamento'].value(),
                self['nacimiento_provincia'].value()),
            initial=None,
            required=False)

        self.fields['residencia_actual_departamento'] = forms.ChoiceField(
            label='Departamento',
            choices=[('', '---------')] +
            self.get_departamentos(),
            initial=None,
            required=False)

        self.fields['residencia_actual_provincia'] = forms.ChoiceField(
            label='Provincias',
            choices=[('', '---------')] +
            self.get_provincias(self['residencia_actual_departamento'].value()),
            initial=None,
            required=False)

        self.fields['residencia_actual_distrito'] = forms.ChoiceField(
            label='Distrito',
            choices=[('', '---------')] +
            self.get_distritos(
                self['residencia_actual_departamento'].value(),
                self['residencia_actual_provincia'].value()),
            initial=None,
            required=False)

        self.fields['centro_poblado_actual'] = forms.ChoiceField(
            label='Localidad',
            choices=[('', '---------')] +
            self.get_localidades(
                self['residencia_actual_departamento'].value(),
                self['residencia_actual_provincia'].value(),
                self['residencia_actual_distrito'].value()),
            initial=None,
            required=False)

    def get_paises(self):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/?page_size=100'.format(settings.MPI_API_HOST)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_pais'], obj['attributes']['ubigeo_pais'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_departamentos(self):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/?page_size=100'.format(settings.MPI_API_HOST)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_departamento'], obj['attributes']['ubigeo_departamento'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_provincias(self, dep_id):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            response = client.get(
                '{}/api/v1/ubigeo/1/177/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id),
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append((
                        obj['attributes']['cod_ubigeo_inei_provincia'],
                        obj['attributes']['ubigeo_provincia']
                    ))
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_distritos(self, dep_id, prov_id):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/{}/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id, prov_id)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_distrito'], obj['attributes']['ubigeo_distrito'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_localidades(self, dep_id, prov_id, dist_id):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/{}/{}/{}/?page_size=100'.format(
                settings.MPI_API_HOST,
                dep_id,
                prov_id,
                dist_id
            )
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_localidad'], obj['attributes']['ubigeo_localidad'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    class Meta:
        model = Paciente
        fields = (
            'tipo_documento', 'numero_documento', 'nombres', 'apellido_paterno', 'apellido_materno',
            'fecha_nacimiento', 'sexo', 'estado_civil', 'nacimiento_pais', 'nacimiento_departamento',
            'nacimiento_provincia', 'nacimiento_distrito', 'residencia_departamento',
            'etnia', 'grado_instruccion', 'ocupacion', 'celular',
            'telefono', 'correo',  'residencia_actual_departamento',
            'residencia_actual_provincia', 'residencia_actual_distrito', 'centro_poblado_actual',
            'direccion_actual', 'referencia_actual', 'longitud', 'latitud',
        )

    def clean_fecha_nacimiento(self):
        if self.cleaned_data.get('fecha_nacimiento') > timezone.now().date():
            raise forms.ValidationError('La fecha de nacimiento no puede ser mayor a la fecha actual')
        return self.cleaned_data.get('fecha_nacimiento')


class PacienteFamiliarForm(forms.ModelForm):
    parentesco = forms.ChoiceField(
        label='Parentesco',
        required=True,
        choices=(('', '-----------------'),) + constants.PARENTESCO_CHOICES
    )

    class Meta:
        model = PacienteContactoFamiliar
        fields = (
            'numero_documento', 'celular', 'correo', 'parentesco'
        )


class HCEForm(forms.ModelForm):
    class Meta:
        model = HCE
        fields = ('numero_hce', 'archivo_clinico')


class ReporteCoberturaForm(forms.Form):
    departamento = forms.ChoiceField(label='Departamento', required=False, widget=forms.Select())
    provincia = forms.ChoiceField(label='Provincia', required=False, widget=forms.Select())
    distrito = forms.ChoiceField(label='Distrito', required=False, widget=forms.Select())
    departamento_nombre = forms.CharField(widget=forms.HiddenInput, required=False)
    provincia_nombre = forms.CharField(widget=forms.HiddenInput, required=False)
    distrito_nombre = forms.CharField(widget=forms.HiddenInput, required=False)
    fecha_inicial = forms.DateField(label='Fecha inicio')
    fecha_final = forms.DateField(label='Fecha fin')

    class Meta:
        model = Brigada
        fields = (
            'nombre', 'ubigeo_departamento', 'ubigeo_provincia', 'ubigeo_distrito',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nacimiento_pais'] = forms.ChoiceField(
            label='Pais',
            choices=[('', '---------')] +
            self.get_paises(), initial=constants.ID_PAIS_PERU, required=False)

        self.fields['departamento'] = forms.ChoiceField(
            label='Departamento',
            choices=[('', '---------')] + self.get_departamentos(), initial=None, required=False)

        self.fields['provincia'] = forms.ChoiceField(
            label='Provincia',
            choices=[('', '---------')] + self.get_provincias(self['departamento'].value()), initial=None,
            required=False)

        self.fields['distrito'] = forms.ChoiceField(
            label='Distrito',
            choices=[('', '---------')] + self.get_distritos(
                        self['departamento'].value(),
                        self['provincia'].value()), initial=None, required=False)

    def get_paises(self):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/?page_size=100'.format(settings.MPI_API_HOST)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_pais'], obj['attributes']['ubigeo_pais'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_departamentos(self):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/?page_size=100'.format(settings.MPI_API_HOST)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_departamento'], obj['attributes']['ubigeo_departamento'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_provincias(self, dep_id):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            response = client.get(
                '{}/api/v1/ubigeo/1/177/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id),
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append((
                        obj['attributes']['cod_ubigeo_inei_provincia'],
                        obj['attributes']['ubigeo_provincia']
                    ))
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def get_distritos(self, dep_id, prov_id):
        client = MPIClient(settings.MPI_API_TOKEN)
        lista_data = []
        try:
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/{}/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id, prov_id)
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or None
                for obj in data:
                    lista_data.append(
                        (obj['attributes']['cod_ubigeo_inei_distrito'], obj['attributes']['ubigeo_distrito'])
                    )
            else:
                lista_data = []
        except Exception as e:
            lista_data = []
            logger.warning('Error al conectar con MPI', exc_info=True)
        return lista_data

    def clean_fecha_inicial(self):
        fecha_inicial = self.cleaned_data.get('fecha_inicial')
        if fecha_inicial > timezone.now().date():
            raise forms.ValidationError('La fecha inicial no puede ser mayor a la fecha actual')
        return fecha_inicial

    def clean_fecha_final(self):
        fecha_final = self.cleaned_data.get('fecha_final')
        if fecha_final > timezone.now().date():
            raise forms.ValidationError('La fecha final no puede ser mayor a la fecha actual')
        return fecha_final
