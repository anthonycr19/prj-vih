from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from mpi_client.client import MPIClient
from django.views.generic import FormView, ListView, CreateView, DetailView, UpdateView
from django.core.urlresolvers import reverse

from apps.common import constants
from apps.common.views import MedicoProtectedView
from apps.common.functions import consulta_servicio_ciudadano_datos_sis_uuid
from apps.afiliacion.models import Paciente

from .forms import (
    TriajeForm, AtencionForm, ExamenAuxForm, AtencionRamForm, AtencionTerapiaForm, ExamenFisicoFormSet,
    AtencionGestacionForm, AtencionDiagnosticoForm, AtencionTratamientoFormSet, DescarteCoinfeccionFormSet, EgresoForm)
from .models import (
    Triaje, Atencion, AtencionRam, ExamenFisico, AtencionControl, AtencionTerapia, AtencionGestacion,
    AtencionFrecuencia, AtencionDiagnostico, AtencionTratamiento, AtencionExamenFisico, AtencionExamenAuxiliar,
    AtencionFrecuenciaControl, AtencionControlXFrecuencia, AtencionDescarteCoinfeccion,
    AtencionFrecuenciaControlDetalle, Egreso)

from django.contrib import messages

from django.utils import timezone


class AtencionIndexView(MedicoProtectedView, FormView):
    template_name = 'atencion/atencion_index.html'
    form_class = AtencionForm

    def get_initial(self):
        return dict(medico=self.username, eess=self.current_establishment)

    def get_form_kwargs(self):
        kwargs = super(AtencionIndexView, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            fecha_registro = timezone.now().date().strftime("%Y-%m-%d")

            if Paciente.objects.filter(paciente__iexact=self.request.POST.get('paciente')).exists():
                paciente = Paciente.objects.get(paciente__iexact=self.request.POST.get('paciente'))
            else:
                ciudadano_phr = servicio_ciudadano_uuid(self.request.POST.get('paciente'))
                if ciudadano_phr['error'] == 'OK':
                    datos_ciudadano = ciudadano_phr['data']
                    paciente = datos_ciudadano
                else:
                    messages.warning(self.request, ciudadano_phr['error'])

            if not self.request.POST.get('cita'):
                cita_uuid = None
                tipo_atencion = constants.TIPO_ATENCION_DEMANDA
            else:
                cita_uuid = self.request.POST.get('cita')
                tipo_atencion = constants.TIPO_ATENCION_CITA

            atencion = Atencion.objects.filter(
                paciente=paciente.paciente,
                eess=self.current_establishment,
                medico=self.username,
                cita_uuid=cita_uuid,
                ups=self.request.POST.get('ups'),
                fecha=fecha_registro
            )
            if atencion:
                atencion = atencion.first()
            else:
                datos_sis = consulta_servicio_ciudadano_datos_sis_uuid(str(paciente.paciente))
                atencion = Atencion()
                atencion.paciente = paciente
                atencion.eess = self.current_establishment
                atencion.medico = self.username
                atencion.cita_uuid = cita_uuid
                atencion.ups = self.request.POST.get('ups')
                atencion.fecha = fecha_registro
                if datos_sis['estado'] == constants.ESTADO_SERVICIO_SIS_TIENE_SIS:
                    atencion.id_financiador = constants.FINANCIADOR_SIS
                    atencion.contrato = datos_sis['contrato']
                    atencion.tipo_seguro = datos_sis['tiposeguro']
                    atencion.tipo_seguro_descripcion = datos_sis['descripcion_tiposeguro']
                    atencion.regimen = datos_sis['regimen']
                    atencion.codigo_eess = datos_sis['codigo_eess']
                    atencion.nombre_eess = datos_sis['nom_eess']
                else:
                    atencion.id_financiador = constants.FINANCIADOR_NO_SE_CONOCE
                atencion.tipo_atencion = tipo_atencion
                atencion.estado_cita = constants.ESTADO_CITA_CONFIRMADO
                atencion.estado_atencion = constants.ESTADO_ATENCION_ATENDIDO
                atencion.save()

            kwargs.update({
                'instance': atencion,
            })

        return kwargs

    def form_valid(self, form):
        obj = form.save()
        return redirect(reverse('atencion:atencion_cita', kwargs={'pk': obj.pk}))


class AtencionCitaView(MedicoProtectedView, DetailView):
    template_name = 'atencion/atencion.html'
    model = Atencion


class AtencionInicialCreateView(MedicoProtectedView, CreateView):
    model = Triaje
    template_name = 'atencion/atencion_inicial.html'
    form_class = TriajeForm
    atencion = None
    formset = None
    flag = 'create'

    def get_initial(self):
        initial = super(AtencionInicialCreateView, self).get_initial()
        self.atencion = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        initial.update({'atencion': self.atencion})
        return initial

    def get_form(self, form_class=None):
        form = super(AtencionInicialCreateView, self).get_form(form_class=form_class)
        if self.request.method in ('POST', 'PUT'):
            self.formset = ExamenFisicoFormSet(self.request.POST, prefix='examen', instance=self.atencion)
        else:
            self.formset = ExamenFisicoFormSet(prefix='examen', instance=self.atencion, initial=ExamenFisico.initial())
        return form

    def form_valid(self, form):
        form.save()
        if self.formset.is_valid():
            self.formset.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.atencion.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(AtencionInicialCreateView, self).get_context_data(**kwargs)
        context.update({
            'formset': self.formset,
            'atencion': self.atencion,
            'edad_paciente': self.atencion.paciente.edad,
            'flag': self.flag,

        })
        return context


class AtencionInicialUpdateView(MedicoProtectedView, UpdateView):
    model = Triaje
    template_name = 'atencion/atencion_inicial.html'
    form_class = TriajeForm
    pk_url_kwarg = 'id'
    atencion = Atencion()
    formset = None
    flag = 'update'

    def get_initial(self):
        initial = super(AtencionInicialUpdateView, self).get_initial()
        self.atencion = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        initial.update({'atencion': self.atencion})
        return initial

    def get_form(self, form_class=None):
        form = super(AtencionInicialUpdateView, self).get_form(form_class=form_class)
        if self.request.method in ('POST', 'UPDATE'):
            self.formset = ExamenFisicoFormSet(self.request.POST, prefix='examen', instance=self.atencion)
        else:
            self.formset = ExamenFisicoFormSet(prefix='examen', instance=self.atencion)
        return form

    def form_valid(self, form):
        form.save()
        if self.formset.is_valid():
            self.formset.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.atencion.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(AtencionInicialUpdateView, self).get_context_data(**kwargs)
        buscar_estado_patalogico = AtencionExamenFisico.objects.filter(atencion=self.atencion, estado='2')
        if buscar_estado_patalogico:
            flag_estado_patalogico = 'Existe'
        else:
            flag_estado_patalogico = 'NoExiste'
        context.update({
            'formset': self.formset,
            'atencion': self.atencion,
            'edad_paciente': self.atencion.paciente.edad,
            'flag': self.flag,
            'flag_estado_patalogico': flag_estado_patalogico,

        })
        return context


class AtencionDxDefinicionCreateView(MedicoProtectedView, CreateView, ListView):
    model = AtencionDiagnostico
    template_name = 'atencion/atencion_dx.html'
    form_class = AtencionDiagnosticoForm
    atencion = Atencion()

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.atencion.get_atencion_definicion_url

    def get_initial(self):
        self.atencion = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        initial = super().get_initial()
        initial.update({
            'atencion': self.atencion
        })
        return initial

    def get_queryset(self):
        return AtencionDiagnostico.objects.filter(atencion__paciente=self.kwargs.get('uuid'))

    def get_context_data(self, **kwargs):
        context = super(AtencionDxDefinicionCreateView, self).get_context_data(**kwargs)
        context.update({'tab': 'dx', 'atencion': self.atencion})
        return context


class AtencionTratamientoCreateView(MedicoProtectedView, FormView, DetailView):
    model = Atencion
    template_name = 'atencion/atencion_dx.html'
    object = None

    def get_object(self, queryset=None):
        self.object = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        return self.object

    def get_form(self, form_class=None):
        if self.request.method in ('POST', 'PUT'):
            return AtencionTratamientoFormSet(self.request.POST, prefix='tarv', instance=self.get_object())
        return AtencionTratamientoFormSet(prefix='tarv')

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.object.get_atencion_tarv_url

    def get_context_data(self, **kwargs):
        context = super(AtencionTratamientoCreateView, self).get_context_data(**kwargs)
        context.update({
            'tab': 'tarv',
            'tratamientos': AtencionTratamiento.objects.filter(atencion__paciente=self.kwargs.get('uuid', None)),
            'atencion': self.object,
        })
        return context


class AtencionGestacionCreateView(CreateView):
    model = AtencionGestacion
    form_class = AtencionGestacionForm
    template_name = 'atencion/atencion_dx.html'
    atencion = None

    def get_initial(self):
        initial = super(AtencionGestacionCreateView, self).get_initial()
        self.atencion = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        initial.update({'atencion': self.atencion})
        return initial

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.atencion.get_atencion_g_url

    def get_context_data(self, **kwargs):
        context = super(AtencionGestacionCreateView, self).get_context_data(**kwargs)
        context.update({
            'tab': 'gestacion',
            'atencion': self.atencion,
        })
        return context


class AtencionTerapiaCreateView(CreateView, ListView):
    model = AtencionTerapia
    form_class = AtencionTerapiaForm
    template_name = 'atencion/atencion_dx.html'
    atencion = None

    def get_initial(self):
        initial = super(AtencionTerapiaCreateView, self).get_initial()
        self.atencion = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        initial.update({'atencion': self.atencion})
        return initial

    def get_queryset(self):
        return self.model.objects.filter(atencion__paciente=self.kwargs.get('uuid'))

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.atencion.get_atencion_terapia_url

    def get_context_data(self, **kwargs):
        context = super(AtencionTerapiaCreateView, self).get_context_data(**kwargs)
        context.update({
            'tab': 'terapia',
            'atencion': self.atencion,
        })
        return context


class AtencionRamCreateView(MedicoProtectedView, CreateView):
    model = AtencionRam
    template_name = 'atencion/atencion_dx.html'
    form_class = AtencionRamForm

    def get_initial(self):
        initial = super(AtencionRamCreateView, self).get_initial()
        self.atencion = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        initial.update({'atencion': self.atencion})
        return initial

    def get_queryset(self):
        return self.model.objects.filter(atencion__paciente=self.kwargs.get('uuid'))

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.atencion.get_atencion_ram_url

    def get_context_data(self, **kwargs):
        context = super(AtencionRamCreateView, self).get_context_data(**kwargs)
        context.update({
            'tab': 'ram',
            'atencion': self.atencion,
            'object_list': self.get_queryset(),
        })
        return context


class ExaAuxiliarCreateView(MedicoProtectedView, CreateView):
    model = AtencionExamenAuxiliar
    template_name = 'atencion/atencion_dx.html'
    form_class = ExamenAuxForm

    def get_initial(self):
        initial = super(ExaAuxiliarCreateView, self).get_initial()
        self.atencion = get_object_or_404(Atencion, pk=self.kwargs.get('pk'))
        initial.update({'atencion': self.atencion})
        return initial

    def get_success_url(self):
        messages.success(self.request, 'Registro realizado con exito.')
        return self.atencion.get_atencion_ex_aux_url

    def get_queryset(self):
        return AtencionExamenAuxiliar.objects.filter(atencion__paciente=self.kwargs.get('uuid'))

    def get_context_data(self, **kwargs):
        context = super(ExaAuxiliarCreateView, self).get_context_data(**kwargs)
        context.update({
            'tab': 'ex-aux',
            'atencion': self.atencion,
            'object_list': self.get_queryset(),
        })
        return context


class DescarteCreateView(MedicoProtectedView):
    model = AtencionDescarteCoinfeccion
    template_name = 'atencion/atencion_descarte.html'
    form_class = DescarteCoinfeccionFormSet
    atencion = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update({
            'atencion': self.get_atencion(kwargs.get('pk')),
            'formset': self.get_formset(request),
            'tb_list': self.model.objects.filter(infeccion=constants.Coinfeccion.TB.value),
            'hpb_list': self.model.objects.filter(infeccion=constants.Coinfeccion.HEPATITISB.value),
            'hpc_list': self.model.objects.filter(infeccion=constants.Coinfeccion.HEPATITISC.value),
        })
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.get_atencion(kwargs.get('pk'))
        formset = self.get_formset(request)
        for form in formset:
            if form.is_valid():
                form.save()
        return redirect(self.atencion.get_atencion_coinfeccion_url)

    def get_formset(self, request):
        if request.method in ('POST', 'PUT'):
            formset = self.form_class(self.request.POST, prefix='coinfeccion', instance=self.atencion)
        else:
            formset = self.form_class(prefix='coinfeccion', instance=self.atencion, initial=[
                {'infeccion': constants.Coinfeccion.TB.value},
                {'infeccion': constants.Coinfeccion.HEPATITISB.value},
                {'infeccion': constants.Coinfeccion.HEPATITISC.value}])
        return formset

    def get_atencion(self, pk):
        if self.atencion is None:
            self.atencion = get_object_or_404(Atencion, pk=pk)
        return self.atencion


class AtencionCronogramaListView(MedicoProtectedView):
    template_name = 'atencion/atencion_cronograma_control.html'

    def get(self, request, *args, **kwargs):
        context = super(AtencionCronogramaListView, self).get_context_data(**kwargs)
        atencion = get_object_or_404(Atencion, pk=kwargs.get('pk'))
        cronograma = AtencionFrecuenciaControl.objects.filter(atencion__paciente=atencion.paciente, estado=1)
        frecuencias = AtencionFrecuencia.objects.all()
        controles = AtencionControl.objects.filter(estado=1)
        context.update({
            'paciente': atencion.paciente,
            'atencion': atencion,
            'cronograma': cronograma,
            'frecuencias': frecuencias,
            'controles': controles
        })
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        atencion = get_object_or_404(Atencion, pk=kwargs.get('pk'))
        if 'btnGenerarCronograma' in request.POST:
            cronograma = AtencionFrecuenciaControl()
            cronograma.paciente = atencion.paciente_id
            cronograma.atencion = atencion
            cronograma.save()
            fecha_hoy = datetime.now()
            for c in AtencionControl.objects.filter(estado=1).order_by('pk'):
                for f in AtencionFrecuencia.objects.all():
                    if self.existe_control_frecuencia(c, f):
                        frecuencia_detalle = AtencionFrecuenciaControlDetalle()
                        frecuencia_detalle.AtencionFrecuencia_control = cronograma
                        frecuencia_detalle.control = c
                        frecuencia_detalle.frecuencia = f
                        frecuencia_detalle.fecha_programada = self.fecha_programada(f, fecha_hoy)
                        frecuencia_detalle.save()
            messages.success(request, 'Se genero el cronograma con Exito.')
        return redirect(atencion.get_atencion_cronograma_url)

    def existe_control_frecuencia(self, control, frecuencia):
        return AtencionControlXFrecuencia.objects.filter(control=control, frecuencia=frecuencia)

    def cantidad_dias(self, f):
        cantidad = AtencionFrecuencia.objects.filter(pk__lte=f.pk).aggregate(Sum('tiempo_dias'))
        return cantidad['tiempo_dias__sum']

    def fecha_programada(self, f, fecha):
        return fecha + timedelta(days=self.cantidad_dias(f))


def servicio_ciudadano_uuid(uuid):
    try:
        mpi_client = MPIClient(settings.MPI_API_TOKEN)
        headers = {
            'Content-Type': 'application/vnd.api+json',
        }
        response = mpi_client.get(
            '{}/api/v1/ciudadano/ver/{}'.format(
                settings.MPI_API_HOST,
                uuid
            ),
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()['data'] if response.json()['data'] else None
            if data:
                nacimiento = data['attributes']['nacimiento_ubigeo']
                if nacimiento:
                    cantidad = len(nacimiento)
                    if (cantidad == 2) or (cantidad == 4) or (cantidad == 6):
                        dep_nac = nacimiento[:2]
                        mpi_client = MPIClient(settings.MPI_API_TOKEN)
                        lista_data_dep = []
                        try:
                            headers = {
                                'Content-Type': 'application/vnd.api+json',
                            }
                            response = mpi_client.get(
                                '{}/api/v1/ubigeo/1/177/{}/?page_size=100&provider=reniec'.format(
                                    settings.MPI_API_HOST,
                                    dep_nac
                                ),
                                headers=headers
                            )
                            if response.status_code == 200:
                                data_dep = response.json()['data'] or None
                                for obj in data_dep:
                                    lista_data_dep.append((obj['attributes']['cod_ubigeo_inei_provincia']))
                            else:
                                lista_data_dep = []
                        except Exception as e:
                            lista_data_dep = []
                        dep_nac_inei = lista_data_dep[0][:2]
                    else:
                        dep_nac_inei = ''
                    if (cantidad == 4) or (cantidad == 6):
                        dep_nac = nacimiento[:2]
                        pro_nac = nacimiento[:4]
                        mpi_client = MPIClient(settings.MPI_API_TOKEN)
                        lista_data_pro = []
                        try:
                            headers = {
                                'Content-Type': 'application/vnd.api+json',
                            }
                            response = mpi_client.get(
                                '{}/api/v1/ubigeo/1/177/{}/{}/?page_size=100&provider=reniec'.format(
                                    settings.MPI_API_HOST,
                                    dep_nac,
                                    pro_nac
                                ),
                                headers=headers
                            )
                            if response.status_code == 200:
                                data_pro = response.json()['data'] or None
                                for obj in data_pro:
                                    lista_data_pro.append((obj['attributes']['cod_ubigeo_inei_distrito']))
                            else:
                                lista_data_pro = []
                        except Exception as e:
                            lista_data_pro = []
                        pro_nac_inei = lista_data_pro[0][:4]
                    else:
                        pro_nac_inei = ''
                    if (cantidad == 6):
                        dis_nac = nacimiento[:6]
                        dep_nac = nacimiento[:2]
                        pro_nac = nacimiento[:4]
                        mpi_client = MPIClient(settings.MPI_API_TOKEN)
                        lista_data_dis = []
                        try:
                            headers = {
                                'Content-Type': 'application/vnd.api+json',
                            }
                            response = mpi_client.get(
                                '{}/api/v1/ubigeo/1/177/{}/{}/{}?page_size=100&provider=reniec'.format(
                                    settings.MPI_API_HOST,
                                    dep_nac,
                                    pro_nac,
                                    dis_nac
                                ),
                                headers=headers
                            )
                            if response.status_code == 200:
                                data_dis = response.json()['data'] or None
                                for obj in data_dis:
                                    lista_data_dis.append((obj['attributes']['cod_ubigeo_inei_localidad']))
                            else:
                                lista_data_dis = []
                        except Exception as e:
                            lista_data_dis = []
                        dis_nac_inei = lista_data_dis[0][:6]
                    else:
                        dis_nac_inei = ''
                else:
                    dep_nac_inei = ''
                    pro_nac_inei = ''
                    dis_nac_inei = ''
                temp = {
                    'paciente': data['attributes']['uid'],
                    'tipo_documento': data['attributes']['tipo_documento'],
                    'numero_documento': data['attributes']['numero_documento'],
                    'apellido_paterno': data['attributes']['apellido_paterno'],
                    'apellido_materno': data['attributes']['apellido_materno'],
                    'nombres': data['attributes']['nombres'],
                    'sexo': data['attributes']['sexo'],
                    'fecha_nacimiento': data['attributes']['fecha_nacimiento'],
                    'telefono': data['attributes']['telefono'],
                    'celular': data['attributes']['celular'],
                    'correo': data['attributes']['correo'],
                    'etnia': data['attributes']['etnia'],
                    'foto': data['attributes']['foto'] or '',
                    'nacimiento_pais': '177',
                    'nacimiento_departamento': dep_nac_inei,
                    'nacimiento_provincia': pro_nac_inei,
                    'nacimiento_distrito': dis_nac_inei,
                    'grado_instruccion': data['attributes']['grado_instruccion'],
                    'ocupacion': data['attributes']['ocupacion'],
                    'residencia_actual_pais': '177',
                    'residencia_actual_departamento': data['attributes'].get('get_departamento_domicilio_ubigeo_inei', ''),  # noqa
                    'residencia_actual_provincia': data['attributes'].get('get_provincia_domicilio_ubigeo_inei', ''),
                    'residencia_actual_distrito': data['attributes'].get('get_distrito_domicilio_ubigeo_inei', ''),
                    'direccion_actual': data['attributes']['domicilio_direccion'] or '',

                }
                Paciente.objects.create(**temp)
                paciente_consulta = Paciente.objects.filter(paciente__iexact=uuid).first()
                data_ciudadano = {
                    'data': paciente_consulta,
                    'error': 'OK'
                }
            else:
                data_ciudadano = {
                    'data': '',
                    'error': 'Paciente no registrado'
                }
        elif response.status_code == 404:
            data_ciudadano = {
                'data': '',
                'error': 'Nro DNI no encontrado en los Servidores, verifique el número'
            }
        else:
            data_ciudadano = {
                'data': '',
                'error': 'Nro DNI no encontrado en los Servidores, verifique el número'
            }
    except ValueError as e:
        data_ciudadano = {
            'data': '',
            'error': 'Paciente no registrado'
        }
    except Exception as e:
        data_ciudadano = {
            'data': '',
            'error': 'Fallo al establecer una conexión con el servicio web de los Ciudadanos'
        }
    return data_ciudadano


class EgresoIndexView(MedicoProtectedView, ListView):
    template_name = 'egreso/egreso_index.html'
    model = Paciente
    context_object_name = 'pacientes'

    def get_queryset(self):
        try:
            qs = super().get_queryset()
            q = self.request.GET.get('q', None)
            if q:
                if q.isdigit():
                    pacientes_otros_documentos = Paciente.objects.filter(
                        numero_documento__iexact=q
                    )
                    if not pacientes_otros_documentos:
                        messages.warning(self.request, 'Nro de documento no encontrado en el Sistema de VIH')
                        qs = qs.none()
                    else:
                        qs = pacientes_otros_documentos
                else:
                    terms = q.split(" ")
                    search = [(Q(nombres__icontains=word) | Q(apellido_paterno__icontains=word) | Q(apellido_materno__icontains=word)) for word in terms]  # noqa
                    paciente_consulta = Paciente.objects.filter(*search)
                    if not paciente_consulta:
                        messages.warning(self.request, 'Nombre no encontrado en el Sistema de VIH')
                        qs = qs.none()
                    else:
                        qs = paciente_consulta
            else:
                qs = qs.none()
            return qs
        except:
            return qs.none()


class EgresoCreateView(MedicoProtectedView, CreateView):
    template_name = 'egreso/crear_egreso.html'
    model = Egreso
    form_class = EgresoForm
    pk_url_kwarg = 'uuid'

    def get_initial(self):
        self.initial.update({
            'eess': self.current_establishment,
            'medico': self.username
        })
        return self.initial.copy()

    def get_form(self, form_class=None):
        fecha_registro = timezone.now().date().strftime("%Y-%m-%d")
        if form_class is None:
            form_class = self.get_form_class()
        paciente = Paciente.objects.get(paciente=self.kwargs.get('uuid', None))

        atencion = Atencion.objects.filter(
            paciente=paciente,
            eess=self.current_establishment,
            medico=self.username,
            cita_uuid=None,
            ups=settings.UPS_EGRESO,
            fecha=fecha_registro
        )
        if atencion.exists():
            atencion = atencion.first()
        else:
            datos_sis = consulta_servicio_ciudadano_datos_sis_uuid(self.kwargs.get('uuid', None))
            atencion = Atencion()
            atencion.paciente = paciente
            atencion.eess = self.current_establishment
            atencion.medico = self.username
            atencion.cita_uuid = None
            atencion.ups = settings.UPS_EGRESO
            atencion.fecha = fecha_registro
            if datos_sis['estado'] == constants.ESTADO_SERVICIO_SIS_TIENE_SIS:
                atencion.id_financiador = constants.FINANCIADOR_SIS
                atencion.contrato = datos_sis['contrato']
                atencion.tipo_seguro = datos_sis['tiposeguro']
                atencion.tipo_seguro_descripcion = datos_sis['descripcion_tiposeguro']
                atencion.regimen = datos_sis['regimen']
                atencion.codigo_eess = datos_sis['codigo_eess']
                atencion.nombre_eess = datos_sis['nom_eess']
            else:
                atencion.id_financiador = constants.FINANCIADOR_NO_SE_CONOCE

            atencion.tipo_atencion = constants.TIPO_ATENCION_CITA
            atencion.estado_cita = constants.ESTADO_CITA_CONFIRMADO
            atencion.estado_atencion = constants.ESTADO_ATENCION_ATENDIDO
            atencion.save()

        datos_kwargs = self.get_form_kwargs()
        datos = self.request.POST.copy()
        datos.update({
            'atencion': atencion,
            'tipo_egreso': constants.TIPO_EGRESO_ABANDONO,
            'fecha_egreso': fecha_registro
        })
        datos_kwargs['data'] = datos
        return form_class(**datos_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = Paciente.objects.get(paciente=self.kwargs.get('uuid', None))
        egreso = Egreso.objects.filter(atencion__paciente__paciente=self.kwargs.get('uuid', None))
        context.update({
            'paciente': paciente,
            'historial_egreso': egreso,
            'ups': settings.UPS_EGRESO
        })
        return context

    def form_invalid(self, form):
        messages.warning(
            self.request,
            'Verifique que los siguientes campos hallan sido llenados {}'.format(form.errors)
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        egreso = form.save(commit=False)
        if not egreso.atencion_id:
            egreso.atencion_id = form.data['atencion'].id
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Registro creado correctamente')
        return reverse('atencion:egreso-crear', kwargs={'uuid': self.kwargs['uuid']})
