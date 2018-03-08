import json

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.urls import reverse
from django.views import generic
from django.views.generic import CreateView, ListView, UpdateView, FormView
from mpi_client.client import MPIClient

from apps.afiliacion.api.views import consulta_servicio_ciudadano_tipodoc
from apps.afiliacion.forms import (BrigadistaForm, HCEForm, PacienteFamiliarForm, PacienteSinDniForm,
    ReporteCoberturaForm)
from apps.afiliacion.models import Brigada, CatalogoEstablecimiento, HCE, Paciente, PacienteContactoFamiliar
from apps.afiliacion.reportes import ReporteUnoExcel
from apps.common.functions import consulta_ver_servicio_ciudadano_uuid, get_edad_completa_str
from apps.common.views import APIProtectedView, BrigadistaAdminProtectedView, EnfermeriaProtectedView, ExcelView


class BrigadaCrearView(BrigadistaAdminProtectedView, generic.CreateView):
#class BrigadaCrearView(generic.CreateView):
    template_name = 'brigada/crear_brigada.html'
    model = Brigada
    form_class = BrigadistaForm

    def form_valid(self, form):
        registro = form.save(commit=False)
        registro.ubigeo_departamento = form.cleaned_data['departamento']
        registro.ubigeo_provincia = form.cleaned_data['provincia']
        registro.ubigeo_distrito = form.cleaned_data['distrito']
        registro.nombre_departamento = form.cleaned_data['departamento_nombre']
        registro.nombre_provincia = form.cleaned_data['provincia_nombre']
        registro.nombre_distrito = form.cleaned_data['distrito_nombre']

        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Datos actualizados correctamente')
        return reverse('afiliacion:crear_brigada')


class AfiliacionView(EnfermeriaProtectedView, generic.TemplateView):
    template_name = 'afiliacion/editar_afiliacion.html'


class PacienteBuscarView(APIProtectedView, ListView):
    template_name = 'paciente/paciente_list.html'
    model = Paciente
    context_object_name = 'pacientes'
    crear_paciente = False
    paciente_nuevo = False
    paciente_continuo = False
    paciente_cnv = False
    establecimiento_afiliado = ""
    establecimiento_logeado = ""
    flag_dni = True
    flag_cnv = False

    def get_queryset(self):
        try:
            qs = super().get_queryset()
            q = self.request.GET.get('q', None)
            id_busqueda = self.request.GET.get('id_busqueda', None)
            establecimiento = self.current_establishment
            consulta_establecimiento = CatalogoEstablecimiento.objects.filter(codigo_renipres=establecimiento)
            try:
                self.establecimiento_logeado = consulta_establecimiento[0].nombre
            except:
                self.establecimiento_logeado = ""

            if q and id_busqueda == 'dni':
                if q.isdigit():
                    qs = self._consulta_numerodocumento(q, establecimiento, qs)
                    self.flag_cnv = False
                else:
                    qs = self._consulta_nombre(q, establecimiento, qs)
                if not qs:
                    digito = len(q)
                    if digito == 8:
                        qs = qs.none()
                        ciudadano_phr = consulta_servicio_ciudadano('01', q)
                        if ciudadano_phr['error'] == 'OK':
                            datos_ciudadano = ciudadano_phr['data']
                            qs = datos_ciudadano
                            self.paciente_nuevo = True
                        else:
                            messages.warning(self.request, ciudadano_phr['error'])
                            self.crear_paciente = True
                    elif digito == 10:
                            qs = self._consulta_servicio_cnv(q, establecimiento, qs)
                    else:
                        messages.warning(self.request, 'Numero de documento no encontrado en los servidores')
                        self.crear_paciente = True
            else:
                if q and id_busqueda == 'cnv':
                    self.crear_paciente = False
                    self.paciente_continuo = False
                    self.paciente_nuevo = False
                    if q.isdigit():
                        qs = self._consulta_servicio_cnv_madre(q, establecimiento, qs)
                    else:
                        messages.warning(self.request, 'Ingrese un Nro DNI Valido')
                else:
                    qs = qs.none()

            return qs
        except:
            return qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        establecimiento = self.current_establishment
        context.update({
            'establecimiento_afiliado': self.establecimiento_afiliado,
            'paciente_nuevo': self.paciente_nuevo,
            'paciente_continuo': self.paciente_continuo,
            'crear_paciente': self.crear_paciente,
            'establecimiento': establecimiento,
            'establecimiento_logeado': self.establecimiento_logeado,
            'flag_dni': self.flag_dni,
            'flag_cnv': self.flag_cnv,
            'paciente_cnv': self.paciente_cnv,
        })
        return context

    def _consulta_numerodocumento(self, q, establecimiento, qs):
        consulta_hce = HCE.objects.filter(
            Q(establecimiento_id=establecimiento),
            Q(paciente__numero_documento__iexact=q) | Q(paciente__numero_documento_cnv__iexact=q)
        )
        if consulta_hce:
            qs = consulta_hce
            self.paciente_continuo = True
        else:
            hce_sin_establecimiento = HCE.objects.filter(
                Q(paciente__numero_documento__iexact=q) | Q(paciente__numero_documento_cnv__iexact=q)
            )
            if hce_sin_establecimiento:
                paciente_consulta = Paciente.objects.filter(
                    Q(numero_documento__iexact=q) | Q(numero_documento_cnv__iexact=q)
                )
                establecimiento = CatalogoEstablecimiento.objects.filter(codigo_renipres=establecimiento)
                try:
                    self.establecimiento_afiliado = establecimiento[0].nombre
                except:
                    self.establecimiento_afiliado = ""

                self.paciente_nuevo = True
                qs = paciente_consulta
            else:
                paciente_consulta = Paciente.objects.filter(
                    Q(numero_documento__iexact=q) | Q(numero_documento_cnv__iexact=q)
                )
                if paciente_consulta:
                    self.paciente_nuevo = True
                    qs = paciente_consulta
                else:
                    qs = qs.none()
        return qs

    def _consulta_nombre(self, q, establecimiento, qs):
        terms = q.split(" ")
        search = [(Q(paciente__nombres__icontains=word) | Q(paciente__apellido_paterno__icontains=word) | Q(paciente__apellido_materno__icontains=word)) for word in terms]  # noqa
        consulta_hce = HCE.objects.filter(*search, establecimiento_id=establecimiento).order_by('-paciente__tipo_documento')  # noqa
        if consulta_hce:
            qs = consulta_hce
            self.paciente_continuo = True
        else:
            hce_sin_establecimiento = HCE.objects.filter(*search)
            if hce_sin_establecimiento:
                paciente_consulta = Paciente.objects.filter(numero_documento__iexact=q)
                establecimiento = CatalogoEstablecimiento.objects.filter(codigo_renipres=establecimiento)
                self.establecimiento_afiliado = establecimiento[0].nombre
                self.paciente_nuevo = True
                qs = paciente_consulta
            else:
                search = [(Q(nombres__icontains=word) | Q(apellido_paterno__icontains=word) | Q(apellido_materno__icontains=word)) for word in terms]  # noqa
                paciente_consulta = Paciente.objects.filter(*search)
                if paciente_consulta:
                    self.paciente_nuevo = True
                    qs = paciente_consulta
                else:
                    qs = qs.none()
        return qs

    def _consulta_servicio_cnv(self, q, establecimiento, qs):
        try:
            mpi_client = MPIClient(settings.MPI_API_TOKEN)
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            response = mpi_client.get(
                '{}/api/v1/cnv/buscar/'.format(settings.MPI_API_HOST),
                params={'q': q},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()['data'][0] if response.json()['data'] else None
                if data:
                    temp = {
                        'id_cnv': data['attributes']['uid'],
                        'numero_documento_cnv': data['attributes']['cui'],
                        'numero_hce': data['attributes']['cui'],
                        'numero_documento_madre': data['attributes']['numero_doc_madre'],
                        'apellido_paterno': data['attributes']['apellido_paterno_ciudadano'],
                        'apellido_materno': data['attributes']['apellido_materno_ciudadano'],
                        'nombres': data['attributes']['nombres_ciudadano'],
                        'sexo': data['attributes']['sexo_nacido'],
                        'fecha_nacimiento': data['attributes']['fecha_nacimiento'],
                        'hora_nacimiento': data['attributes']['hora_nacimiento'],
                        'etnia': data['attributes']['etnia_nacido'],
                        'tipo_documento_madre': data['attributes']['tipo_doc_madre'],
                        'id_phr': data['attributes']['ciudadano_uuid'],
                        'tipo_documento': data['attributes']['ciudadano_tipo_doc'],
                        'numero_documento': data['attributes']['ciudadano_numero_doc'],
                        'cnv_activo': True
                    }
                    Paciente.objects.create(**temp)
                    paciente_consulta = Paciente.objects.filter(numero_documento_cnv__iexact=q)
                    qs = paciente_consulta
                    self.paciente_nuevo = True
                else:
                    messages.success(self.request, 'Paciente no registrado')
                    self.crear_paciente = True
            elif response.status_code == 404:
                messages.warning(self.request, 'Recurso no encontrado en MPI')
            else:
                messages.warning(self.request, 'Error de conexion con MPI')
        except ValueError as e:
            messages.success(self.request, 'Paciente no registrado')
            qs = qs.none()
        except Exception as e:
            messages.warning(self.request, 'Fallo al establecer una conexión con el servicio web de MPI')
        return qs

    def _consulta_servicio_cnv_madre(self, q, establecimiento, qs):
        try:
            mpi_client = MPIClient(settings.MPI_API_TOKEN)
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            response = mpi_client.get('{}/api/v1/cnv/madre/01/{}/'.format(settings.MPI_API_HOST, q), headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] if response.json()['data'] else None
                if data:
                    datos = []
                    for dato in data:
                        existe_paciente = Paciente.objects.filter(
                            Q(paciente__iexact=dato['attributes']['ciudadano_uuid'])
                        )
                        if existe_paciente:
                            id_paciente = existe_paciente[0].paciente
                            consulta_hce = HCE.objects.filter(
                                Q(establecimiento_id=establecimiento),
                                Q(paciente__paciente__iexact=dato['attributes']['ciudadano_uuid'])
                            )
                            if consulta_hce:
                                cnv_activo = existe_paciente[0].cnv_activo

                                if cnv_activo:
                                    estado_paciente = '1'
                                    dni_activo = ''
                                    dni_rn = ''
                                else:
                                    estado_paciente = '3'
                                    existe_paciente_dni = Paciente.objects.filter(
                                        Q(tipo_documento__iexact='01'),
                                        Q(numero_documento_cnv__iexact=dato['attributes']['cui'])
                                    ).first()
                                    dni_activo = existe_paciente_dni.paciente
                                    dni_rn = existe_paciente_dni.numero_documento
                            else:
                                estado_paciente = '2'
                                cnv_activo = existe_paciente[0].cnv_activo
                                dni_activo = ''
                                dni_rn = ''
                            apellido_paterno = existe_paciente[0].apellido_paterno
                            apellido_materno = existe_paciente[0].apellido_materno
                            nombres = existe_paciente[0].nombres
                        else:

                            if dato['attributes']['ciudadano_tipo_doc'] == '00':
                                estado_cnv = True
                                estado_paciente = '2'
                                id_paciente_rn = ''
                                dni_paciente_rn = ''
                                temp = {
                                    'paciente': dato['attributes']['ciudadano_uuid'],
                                    'uid_cnv': dato['attributes']['uid'],
                                    'numero_documento_cnv': dato['attributes']['cui'],
                                    'numero_documento_madre': dato['attributes']['numero_doc_madre'],
                                    'apellido_paterno': dato['attributes']['apellido_paterno_ciudadano'],
                                    'apellido_materno': dato['attributes']['apellido_materno_ciudadano'],
                                    'nombres': dato['attributes']['nombres_ciudadano'],
                                    'sexo': dato['attributes']['sexo_nacido'],
                                    'fecha_nacimiento': dato['attributes']['fecha_nacimiento'],
                                    'hora_nacimiento': dato['attributes']['hora_nacimiento'],
                                    'etnia': dato['attributes']['etnia_nacido'],
                                    'tipo_documento': dato['attributes']['ciudadano_tipo_doc'],
                                    'numero_documento': dato['attributes']['ciudadano_numero_doc'],
                                    'tipo_documento_madre': dato['attributes']['tipo_doc_madre'],
                                    'cnv_activo': estado_cnv
                                }
                                Paciente.objects.create(**temp)
                                paciente_consulta = Paciente.objects.get(
                                    paciente__iexact=dato['attributes']['ciudadano_uuid']
                                )
                                id_paciente_uid = paciente_consulta.paciente

                            if dato['attributes']['ciudadano_tipo_doc'] == '01':
                                estado_cnv = False
                                ciudadano_phr = consulta_servicio_ciudadano(
                                    '01',
                                    dato['attributes']['ciudadano_numero_doc']
                                )
                                if ciudadano_phr['error'] == 'OK':
                                    estado_paciente = '3'
                                    existe_paciente_dni = Paciente.objects.filter(
                                        Q(tipo_documento__iexact='01'),
                                        Q(numero_documento__iexact=dato['attributes']['ciudadano_numero_doc'])
                                    ).first()
                                    id_paciente_rn = existe_paciente_dni.paciente
                                    dni_paciente_rn = existe_paciente_dni.numero_documento
                                    id_paciente_uid = existe_paciente_dni.paciente

                                    Paciente.objects.filter(paciente=id_paciente_rn).update(
                                        paciente=dato['attributes']['ciudadano_uuid'],
                                        uid_cnv=dato['attributes']['uid'],
                                        numero_documento_cnv=dato['attributes']['cui'],
                                        numero_documento_madre=dato['attributes']['numero_doc_madre'],
                                        apellido_paterno=dato['attributes']['apellido_paterno_ciudadano'],
                                        apellido_materno=dato['attributes']['apellido_materno_ciudadano'],
                                        nombres=dato['attributes']['nombres_ciudadano'],
                                        sexo=dato['attributes']['sexo_nacido'],
                                        fecha_nacimiento=dato['attributes']['fecha_nacimiento'],
                                        hora_nacimiento=dato['attributes']['hora_nacimiento'],
                                        etnia=dato['attributes']['etnia_nacido'],
                                        tipo_documento=dato['attributes']['ciudadano_tipo_doc'],
                                        numero_documento=dato['attributes']['ciudadano_numero_doc'],
                                        tipo_documento_madre=dato['attributes']['tipo_doc_madre'],
                                        cnv_activo=estado_cnv,
                                    )
                                else:
                                    messages.warning(self.request, ciudadano_phr['error'])
                            id_paciente = id_paciente_uid
                            apellido_paterno = dato['attributes']['apellido_paterno_ciudadano']
                            apellido_materno = dato['attributes']['apellido_materno_ciudadano']
                            nombres = dato['attributes']['nombres_ciudadano']
                            cnv_activo = estado_cnv
                            dni_activo = id_paciente_rn
                            dni_rn = dni_paciente_rn
                        datos.append({
                            'uid_cnv': dato['attributes']['uid'],
                            'numero_documento_cnv': dato['attributes']['cui'],
                            'numero_hce': dato['attributes']['cui'],
                            'numero_documento_madre': dato['attributes']['numero_doc_madre'],
                            'apellido_paterno': apellido_paterno,
                            'apellido_materno': apellido_materno,
                            'nombres': nombres,
                            'sexo': dato['attributes']['sexo_nacido'],
                            'fecha_nacimiento': dato['attributes']['fecha_nacimiento'],
                            'hora_nacimiento': dato['attributes']['hora_nacimiento'],
                            'etnia': dato['attributes']['etnia_nacido'],
                            'paciente': dato['attributes']['ciudadano_uuid'],
                            'tipo_documento': dato['attributes']['ciudadano_tipo_doc'],
                            'numero_documento': dato['attributes']['ciudadano_numero_doc'],
                            'tipo_documento_madre': dato['attributes']['tipo_doc_madre'],
                            'estado': estado_paciente,
                            'id_paciente': id_paciente,
                            'cnv_activo': cnv_activo,
                            'dni_activo': dni_activo,
                            'dni_rn': dni_rn,
                            'edad_str': get_edad_completa_str(dato['attributes']['fecha_nacimiento'])
                        })
                    self.flag_cnv = True
                    self.flag_dni = False
                    self.paciente_cnv = True
                    qs = datos
                else:
                    messages.success(
                        self.request,
                        'El DNI: ' + q + ' de la Mamá no tiene asignado CNV, verifique si es el correcto.'
                    )
                    self.flag_cnv = True
                    self.flag_dni = False
            elif response.status_code == 404:
                messages.warning(
                    self.request,
                    'El DNI no se encuentra en nuestros Servidores, verifique si es el correcto.'
                )
            else:
                messages.warning(self.request, 'Error de conexion con el Servidor, intente mas tarde.')
        except ValueError as e:
            messages.success(self.request, 'Paciente no registrado')
            qs = qs.none()
        except Exception as e:
            messages.warning(self.request, 'Fallo al establecer una conexión con el servicio web de MPI')
        return qs


class PacienteUpdateView(EnfermeriaProtectedView, UpdateView):
    template_name = 'paciente/paciente_editar.html'
    model = Paciente
    form_class = PacienteSinDniForm
    pk_url_kwarg = 'paciente_id'
    object = None
    paciente = None

    def dispatch(self, request, *args, **kwargs):
        self.paciente = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if self.object is None:
            self.object = super().get_object(queryset)
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = Paciente.objects.get(pk=self.kwargs['paciente_id'])
        establecimiento_actual = self.current_establishment
        historia = HCE.objects.filter(
            Q(paciente__numero_documento__iexact=paciente.numero_documento, establecimiento__codigo_renipres=establecimiento_actual)  # noqa
        ).first()
        form_hce = HCEForm(self.request.POST or None, instance=historia)
        context.update({
            'paciente': paciente,
            'historia': historia,
            'form_hce': form_hce
        })
        return context

    def form_valid(self, form):
        paciente = Paciente.objects.filter(Q(paciente=self.request.POST['id_paciente'])).first()
        context = self.get_context_data()
        form_hce = context['form_hce']
        establecimiento_actual = self.current_establishment
        existe_est = CatalogoEstablecimiento.objects.filter(codigo_renipres__iexact=establecimiento_actual)
        if existe_est:
            establecimiento = CatalogoEstablecimiento.objects.get(codigo_renipres=establecimiento_actual)
            obj_establecimiento = establecimiento
        else:
            phr_establecimiento = servicio_phr_por_establecimiento(establecimiento_actual)
            obj_establecimiento = phr_establecimiento
        registro = form_hce.save(commit=False)
        registro.establecimiento = obj_establecimiento
        registro.paciente = paciente
        if form_hce.is_valid() and form.is_valid():
            hce = HCE.objects.filter(
                Q(paciente_id=self.request.POST['id_paciente'], establecimiento__codigo_renipres=establecimiento_actual)
            ).first()

            if hce:
                HCE.objects.filter(id=hce.id).update(
                    numero_hce=form_hce.cleaned_data['numero_hce'],
                    archivo_clinico=form_hce.cleaned_data['archivo_clinico'],
                )
                return super().form_valid(form)
            else:
                registro.save()
                return super().form_valid(registro)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.warning(self.request,
                         'Ocurrió un error, verifique que todos los campos obligatorios han sido llenados')
        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, 'Datos actualizados correctamente')
        return reverse('afiliacion:editar_paciente', kwargs={'paciente_id': self.paciente.paciente})


def consulta_servicio_ciudadano(tipo_documento, q):
    try:
        mpi_client = MPIClient(settings.MPI_API_TOKEN)
        headers = {
            'Content-Type': 'application/vnd.api+json',
        }
        response = mpi_client.get(
            '{}/api/v1/ciudadano/ver/{}/{}'.format(
                settings.MPI_API_HOST,
                tipo_documento,
                q
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
                paciente_consulta = Paciente.objects.filter(numero_documento__iexact=q)
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


class PacienteCreateView(EnfermeriaProtectedView, CreateView):
    template_name = 'paciente/paciente_create.html'
    model = Paciente
    form_class = PacienteSinDniForm
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        messages.warning(self.request,
                         'Ocurrió un error, verifique que todos los campos obligatorios han sido llenados')
        return super().form_invalid(form)

    def form_valid(self, form):
        mpi_client = MPIClient(settings.MPI_API_TOKEN)
        nacimiento = form.cleaned_data['fecha_nacimiento'].strftime('%Y-%m-%d')
        data = {
            'nombres': form.cleaned_data['nombres'],
            'apellido_paterno': form.cleaned_data['apellido_paterno'],
            'apellido_materno': form.cleaned_data['apellido_materno'],
            'sexo': form.cleaned_data['sexo'],
            'fecha_nacimiento': nacimiento,
            'grado_instruccion': form.cleaned_data['grado_instruccion'],
            'ocupacion': form.cleaned_data['ocupacion'],
            'etnia': form.cleaned_data['etnia'],
            'tipo_documento': form.cleaned_data['tipo_documento'],
            'numero_documento': form.cleaned_data['numero_documento'],
            'estado_civil': form.cleaned_data['estado_civil'],
            'nacimiento_pais': form.cleaned_data['nacimiento_pais'],
            'nacimiento_departamento': form.cleaned_data['nacimiento_departamento'],
            'nacimiento_provincia': form.cleaned_data['nacimiento_provincia'],
            'nacimiento_distrito': form.cleaned_data['nacimiento_distrito'],
        }
        response = mpi_client.post('{}/api/v1/ciudadano/crear/'.format(settings.MPI_API_HOST), data=data)
        if response.status_code == 201:
            data = response.json()['data']
            datos = response.text
            datos_paciente = json.loads(datos)
            form.save(commit=False)
            paciente = Paciente(
                paciente=datos_paciente['data']['attributes']['uuid'],
                tipo_documento=datos_paciente['data']['attributes']['tipo_documento'],
                numero_documento=datos_paciente['data']['attributes']['numero_documento'],
                apellido_paterno=datos_paciente['data']['attributes']['apellido_paterno'],
                apellido_materno=datos_paciente['data']['attributes']['apellido_materno'],
                nombres=datos_paciente['data']['attributes']['nombres'],
                sexo=datos_paciente['data']['attributes']['sexo'],
                fecha_nacimiento=datos_paciente['data']['attributes']['fecha_nacimiento'],
                etnia=datos_paciente['data']['attributes']['etnia'],
                foto=datos_paciente['data']['attributes']['foto'],
                nacimiento_pais='177',
                nacimiento_departamento=form.cleaned_data['nacimiento_departamento'],
                nacimiento_provincia=form.cleaned_data['nacimiento_provincia'],
                nacimiento_distrito=form.cleaned_data['nacimiento_distrito'],
                estado_civil=datos_paciente['data']['attributes']['estado_civil'],
                grado_instruccion=datos_paciente['data']['attributes']['grado_instruccion'],
                ocupacion=datos_paciente['data']['attributes']['ocupacion'],
            )
            paciente.save()
            paciente_consulta = Paciente.objects.get(
                paciente__iexact=datos_paciente['data']['attributes']['uuid']
            )
            self.id_paciente = paciente_consulta.paciente
        else:
            messages.warning(self.request, 'Error al conectarse con MPI')
            return HttpResponseRedirect(reverse('pacientes:paciente_list'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self, **kwargs):
        messages.success(self.request, 'Datos creados, puede actualizar algunos datos adicionales')
        return reverse('afiliacion:editar_paciente', kwargs={'paciente_id': self.id_paciente})


class PacienteListFamiliaView(ListView):
    template_name = 'paciente/contacto_familia/paciente_familia.html'
    model = PacienteContactoFamiliar
    form_class = PacienteFamiliarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = Paciente.objects.filter(numero_documento=self.kwargs['dni_paciente']).first()
        id_paciente = paciente.paciente
        familiares = PacienteContactoFamiliar.objects.filter(paciente_id=id_paciente)
        context.update({
            'id_paciente': id_paciente,
            'form3': self.form_class(),
            'familiares': familiares
        })
        return context


class PacienteBuscarFamiliaView(CreateView):
    template_name = 'paciente/contacto_familia/paciente_familia_buscar.html'
    model = PacienteContactoFamiliar
    form_class = PacienteFamiliarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_paciente = self.kwargs['paciente_id']
        context.update({
            'id_paciente': id_paciente,
            'form_familiar': self.form_class()
        })
        return context


class PacienteResultadoBuscarFamiliaView(CreateView):
    template_name = 'paciente/contacto_familia/paciente_familia_resultado_buscar.html'
    model = PacienteContactoFamiliar
    form_class = PacienteFamiliarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dni = self.request.GET['dni']
        id_paciente = self.request.GET['id_paciente']
        ciudadano = consulta_servicio_ciudadano_tipodoc(dni, '01')
        context.update({
            'id_paciente': id_paciente,
            'dni': dni,
            'form_familiar': self.form_class(),
            'pacientes': ciudadano
        })
        return context


class PacienteGuardarFamiliaView(CreateView):
    template_name = 'paciente/contacto_familia/form_paciente_familia_crear.html'
    model = PacienteContactoFamiliar
    form_class = PacienteFamiliarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nrodoc = self.kwargs['dni_paciente']
        id_paciente = self.kwargs['paciente_id']
        form_class = PacienteFamiliarForm(initial={
            'numero_documento': nrodoc,
        })
        context.update({
            'id_paciente': id_paciente,
            'nrodoc': nrodoc,
            'form_familiar': form_class
        })
        return context

    def form_invalid(self, form):
        messages.warning(self.request,
                         'Ocurrió un error, verifique que todos los campos obligatorios han sido llenados '
                         '(Los campos obligatorios se encuentran resaltados con letras rojas')
        return super().form_invalid(form)

    def form_valid(self, form, *args, **kwargs):
        paciente = Paciente.objects.filter(Q(paciente=self.request.POST['id_paciente'])).first()
        ciudadano = consulta_servicio_ciudadano_tipodoc(self.request.POST['numero_documento'], '01')
        if ciudadano['error'] == 'OK':
            registro = form.save(commit=False)
            registro.paciente = paciente
            registro.id_phr_familiar = ciudadano['data']['uid']
            registro.tipo_documento = ciudadano['data']['tipo_documento']
            registro.apellido_paterno = ciudadano['data']['apellido_paterno']
            registro.apellido_materno = ciudadano['data']['apellido_materno']
            registro.nombres = ciudadano['data']['nombres']
            registro.sexo = ciudadano['data']['sexo']
            paciente_familiar = PacienteContactoFamiliar.objects.filter(
                Q(paciente=paciente),
                Q(tipo_documento=ciudadano['data']['tipo_documento']),
                Q(numero_documento=ciudadano['data']['numero_documento']),
            ).first()

            if paciente_familiar:
                messages.warning(self.request, 'Datos del Familiar ya registrados.')
                return HttpResponseRedirect(reverse(
                    'afiliacion:editar_paciente',
                    kwargs={'paciente_id': self.request.POST['id_paciente']}
                ))
            else:
                if ciudadano['data']['numero_documento'] == paciente.numero_documento:
                    messages.warning(self.request, 'Estos datos son de la misma persona.')
                    return HttpResponseRedirect(reverse(
                        'afiliacion:editar_paciente',
                        kwargs={'paciente_id': self.request.POST['id_paciente']}
                    ))
                else:
                    if form.is_valid():
                        return super().form_valid(registro)
                    else:
                        return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, **kwargs):
        messages.success(self.request, 'Datos guardados correctamente.')
        return reverse('afiliacion:editar_paciente', kwargs={'paciente_id': self.request.POST['id_paciente']})


def eliminar_datos_familia_view(request, id_contactofamilia):
    if request.method == 'GET':
        PacienteContactoFamiliar.objects.get(id=id_contactofamilia).delete()
        datos = {'resultado': 'Datos Eliminados correctamente.'}
        return render_to_response('paciente/contacto_familia/paciente_familia_eliminar.html', datos)
    else:
        return HttpResponse('', status=405)


def servicio_phr_por_establecimiento(establecimiento_actual):
    try:
        phr_establecimiento = []
        mpi_client = MPIClient(settings.MPI_API_TOKEN)
        headers = {
            'Content-Type': 'application/vnd.api+json',
        }
        response = mpi_client.get(
            '{}/api/v1/establecimiento/{}/'.format(
                settings.MPI_API_HOST,
                establecimiento_actual
            ),
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()['data'] if response.json()['data'] else None
            if data:
                temp = {
                    'codigo_renipres': data['attributes']['codigo_renaes'],
                    'nombre': data['attributes']['nombre'],
                    'ubigeo': data['attributes']['ubigeo'],
                    'categoria_cod': data['attributes']['categoria_nivel'],
                    'sector_codigo': data['attributes']['sector_codigo'],
                    'diresa': data['attributes']['diresa_codigo'],
                    'red': data['attributes']['red_codigo'],
                    'microred': data['attributes']['microred_codigo'],
                    'latitude': data['attributes'].get('location.latitude', ''),
                    'longitude': data['attributes'].get('location.latitude', ''),
                    'nombre_red': data['attributes']['red_nombre'],
                    'nombre_microred': data['attributes']['microred_nombre'],
                    'nombre_sector': data['attributes']['sector_nombre'],
                }
                CatalogoEstablecimiento.objects.create(**temp)
                phr_establecimiento = CatalogoEstablecimiento.objects.get(codigo_renipres=establecimiento_actual)
            else:
                phr_establecimiento = phr_establecimiento.none()
        elif response.status_code == 404:
            phr_establecimiento = phr_establecimiento.none()
        else:
            phr_establecimiento = phr_establecimiento.none()
    except ValueError as e:
        phr_establecimiento = phr_establecimiento.none()
    except Exception as e:
        phr_establecimiento = phr_establecimiento.none()
    return phr_establecimiento


def verpaciente(request):
    q = request.GET.get('q')
    lista_data = []
    if q.isdigit():
        buscar_paciente = Paciente.objects.filter(tipo_documento='01', numero_documento=q)
        if buscar_paciente:
            data = buscar_paciente
            for obj in data:
                lista_data.append({
                    'uuid': obj.paciente,
                    'nombres': obj.nombres,
                    'apellido_paterno': obj.apellido_paterno,
                    'apellido_materno': obj.apellido_materno,
                    'tipo_documento': obj.tipo_documento,
                    'numero_documento': obj.numero_documento
                })
        else:
            buscar_mpi = consulta_ver_servicio_ciudadano_uuid(q)
            if buscar_mpi['resultado'] == 'OK':
                data = buscar_mpi['data']
                lista_data = [{
                    'uuid':  buscar_mpi['data']['uid'],
                    'nombres':  buscar_mpi['data']['nombres'],
                    'apellido_paterno':  buscar_mpi['data']['apellido_paterno'],
                    'apellido_materno':  buscar_mpi['data']['apellido_materno'],
                    'tipo_documento':  '01',
                    'numero_documento': buscar_mpi['data']['numero_documento']
                }]
            else:
                lista_data = []
    else:
        if q:
            terms = q.split(" ")
            search = [(Q(nombres__icontains=word) | Q(apellido_paterno__icontains=word) | Q(apellido_materno__icontains=word)) for word in terms]  # noqa
            data = Paciente.objects.filter(*search)
            for obj in data:
                lista_data.append({
                    'uuid': obj.paciente,
                    'nombres': obj.nombres,
                    'apellido_paterno': obj.apellido_paterno,
                    'apellido_materno': obj.apellido_materno,
                    'tipo_documento': obj.tipo_documento,
                    'numero_documento': obj.numero_documento
                })

    return JsonResponse({'data': lista_data})


class ConsolidadoExcelView(ExcelView, FormView):
    form_class = ReporteCoberturaForm
    filename = 'consolidado_del_{}_al_{}.xlsx'
    departamento = None
    provincia = None
    distrito = None
    brigada = None
    fecha_inicial = None
    fecha_final = None
    template_name = 'reportes/reporte_consolidado.html'

    def form_valid(self, form):
        self.departamento = form.cleaned_data['departamento']
        self.provincia = form.cleaned_data['provincia']
        self.distrito = form.cleaned_data['distrito']
        self.fecha_inicial = form.cleaned_data['fecha_inicial']
        self.fecha_final = form.cleaned_data['fecha_final']
        self.filename = self.filename.format(self.fecha_inicial, self.fecha_final)

        return self.render_excel_to_response()

    def get_book(self, output):
        report = ReporteUnoExcel(self.departamento, self.provincia, self.distrito)
        return report.get_book(output)
