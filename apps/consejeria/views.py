from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, RedirectView, TemplateView

from apps.common import constants
from apps.common.views import EnfermeriaProtectedView
from apps.atencion.models import Atencion
from apps.common.functions import consulta_servicio_ciudadano_datos_sis_uuid
from apps.afiliacion.models import Paciente, Poblacion
from apps.consejeria.models import Consejeria, ConsejeriaPost
from apps.afiliacion.api.views import get_cita

from .forms import ConsejeriPostForm

from django.contrib import messages

from django.utils import timezone


class ConsejeriaPreIndex(EnfermeriaProtectedView, TemplateView):
    template_name = 'consejeria/consejeria_pre_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'poblaciones': Poblacion.objects.all(),
        })
        return context


class ConsejeriaPostIndex(EnfermeriaProtectedView, CreateView):
    template_name = 'consejeria/consejeria_post_index.html'
    form_class = ConsejeriPostForm
    success_url = reverse_lazy('consejeria:consejeria_post_index')

    def get_initial(self):
        self.initial.update({
            'eess': self.current_establishment,
            'medico': self.username,
        })
        return self.initial.copy()


class CrearConsejeriaPostIndex(EnfermeriaProtectedView, CreateView):
    template_name = 'consejeria/crear_consejeria_post.html'
    model = ConsejeriaPost
    form_class = ConsejeriPostForm
    pk_url_kwarg = 'uuid'

    def get_initial(self):
        self.initial.update({
            'eess': self.current_establishment,
            'medico': self.username,
        })
        return self.initial.copy()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        cita_uuid = self.kwargs.get('uuid', None)
        datos_cita = get_cita(cita_uuid)
        datos_kwargs = self.get_form_kwargs()
        datos = self.request.POST.copy()
        datos.update({
            'paciente': datos_cita['id_phr_paciente'],
            'cita': datos_cita['uuid_cita'],
            'eess': self.current_establishment,
            'medico': self.username,
            'ups': datos_cita['cod_ups'],
            'via_transmision': 'sexual',
            'antecedentes': 'RSVARON',
            'nro_parejas': 1
        })
        datos_kwargs['data'] = datos
        return form_class(**datos_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'cita_uuid': self.kwargs['uuid'],
        })
        return context

    def form_invalid(self, form):
        messages.warning(
            self.request,
            'Verifique que los campos obligatorios han sido llenados'
        )
        return super().form_invalid(form)

    def form_valid(self, form, *args, **kwargs):
        form.save(commit=False)
        uuid_paciente = form.data['paciente']
        medico = form.data['medico']
        cita = form.data['cita']
        eess = form.data['eess']
        ups = form.data['ups']
        fecha_actual = timezone.now().date()
        fecha_registro = fecha_actual.strftime("%Y-%m-%d")
        try:
            paciente = Paciente.objects.get(paciente=uuid_paciente)
        except Paciente.DoesNotExist:
            messages.warning(self.request,
                             'Error al recuperar los datos del paciente comuniquese con el administrador')
            return redirect('consejeria:crear_consejeria_post', uuid=self.kwargs['uuid'])
        atencion = Atencion.objects.filter(
            paciente=paciente,
            eess=eess,
            medico=medico,
            cita_uuid=cita,
            ups=ups,
            fecha=fecha_registro
        )
        if atencion.exists():
            atencion = atencion.first()
            consejeria = Consejeria.objects.filter(atencion=atencion.id)
            if consejeria:
                messages.warning(self.request, 'Error, ya se tiene registrado una post consejeria')
                return redirect('consejeria:crear_consejeria_post', uuid=self.kwargs['uuid'])
            else:
                consejeria = Consejeria()
                consejeria.atencion = atencion
                consejeria.tipo_consejeria = constants.POST
                consejeria.fecha_registro = fecha_registro
                consejeria.save()

                consejeriapost = ConsejeriaPost()
                consejeriapost.consejeria = consejeria
                consejeriapost.via_transmision = form.cleaned_data.get('via_transmision')
                consejeriapost.antecedentes = form.cleaned_data.get('antecedentes')
                consejeriapost.tipo_transmision = form.cleaned_data.get('tipo_transmision')
                consejeriapost.nro_parejas = form.cleaned_data.get('nro_parejas')
                consejeriapost.uso_preservativo = form.cleaned_data.get('uso_preservativo')
                consejeriapost.save()
        else:
            datos_sis = consulta_servicio_ciudadano_datos_sis_uuid(uuid_paciente)
            atencion = Atencion()
            atencion.paciente = paciente
            atencion.eess = eess
            atencion.medico = medico
            atencion.cita_uuid = cita
            atencion.ups = ups
            atencion.fecha = fecha_registro
            if datos_sis['estado'] == '1':
                atencion.id_financiador = constants.FINANCIADOR_SIS
                atencion.contrato = datos_sis['contrato']
                atencion.tipo_seguro = datos_sis['tiposeguro']
                atencion.tipo_seguro_descripcion = datos_sis['descripcion_tiposeguro']
                atencion.regimen = datos_sis['regimen']
                atencion.codigo_eess = datos_sis['codigo_eess']
                atencion.nombre_eess = datos_sis['nom_eess']
            else:
                atencion.id_financiador = constants.FINANCIADOR_NO_SE_CONOCE
                atencion.contrato = ''
                atencion.tipo_seguro = ''
                atencion.tipo_seguro_descripcion = ''
                atencion.regimen = ''
                atencion.codigo_eess = ''
                atencion.nombre_eess = ''
            atencion.tipo_atencion = constants.TIPO_ATENCION_CITA
            atencion.estado_cita = constants.ESTADO_CITA_CONFIRMADO
            atencion.estado_atencion = constants.ESTADO_ATENCION_ATENDIDO
            atencion.save()

            consejeria = Consejeria()
            consejeria.atencion = atencion
            consejeria.tipo_consejeria = constants.POST
            consejeria.fecha_registro = fecha_registro
            consejeria.save()

            consejeriapost = ConsejeriaPost()
            consejeriapost.consejeria = consejeria
            consejeriapost.via_transmision = form.cleaned_data.get('via_transmision')
            consejeriapost.antecedentes = form.cleaned_data.get('antecedentes')
            consejeriapost.tipo_transmision = form.cleaned_data.get('tipo_transmision')
            consejeriapost.nro_parejas = form.cleaned_data.get('nro_parejas')
            consejeriapost.uso_preservativo = form.cleaned_data.get('uso_preservativo')
            consejeriapost.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, 'Registro creado correctamente')
        return reverse('consejeria:crear_consejeria_post', kwargs={'uuid': self.kwargs['uuid']})


class EditarConsejeriaPostIndex(EnfermeriaProtectedView, UpdateView):
    template_name = 'consejeria/editar_consejeria_post.html'
    model = ConsejeriaPost
    form_class = ConsejeriPostForm
    pk_url_kwarg = 'id'

    def get_initial(self):
        self.initial.update({
            'eess': self.current_establishment,
            'medico': self.username,
        })
        return self.initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consejeria_id = ConsejeriaPost.objects.values('consejeria_id').filter(id=self.kwargs['id'])
        atencion_id = Consejeria.objects.values('atencion_id').filter(id=consejeria_id)
        atencion = Atencion.objects.get(id=atencion_id)
        context.update({
            'cita_uuid': atencion.cita_uuid,
            'atencion': atencion
        })
        return context

    def post(self, request, *args, **kwargs):
        consejeria_id = ConsejeriaPost.objects.values('consejeria_id').filter(id=self.kwargs['id'])
        atencion_id = Consejeria.objects.values('atencion_id').filter(id=consejeria_id)
        atencion = Atencion.objects.get(id=atencion_id)
        form = ConsejeriPostForm(request.POST.copy())
        form.data['paciente'] = atencion.paciente.paciente
        form.data['cita'] = atencion.cita_uuid
        form.data['eess'] = atencion.eess
        form.data['medico'] = atencion.medico
        form.data['ups'] = atencion.ups
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, *args, **kwargs):
        form.save(commit=False)
        ConsejeriaPost.objects.filter(id=self.kwargs['id']).update(
            via_transmision=form.cleaned_data.get('via_transmision'),
            antecedentes=form.cleaned_data.get('antecedentes'),
            tipo_transmision=form.cleaned_data.get('tipo_transmision'),
            nro_parejas=form.cleaned_data.get('nro_parejas'),
            uso_preservativo=form.cleaned_data.get('uso_preservativo'),
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.warning(
            self.request,
            'Verifique que los campos obligatorios han sido llenados'
        )
        return super().form_invalid(form)

    def get_success_url(self):
        consejeria_id = ConsejeriaPost.objects.values('consejeria_id').filter(id=self.kwargs['id'])
        atencion_id = Consejeria.objects.values('atencion_id').filter(id=consejeria_id)
        cita_uuid = Atencion.objects.values('cita_uuid').get(id=atencion_id)
        messages.success(self.request, 'Datos actualizados correctamente')
        return reverse('consejeria:crear_consejeria_post', kwargs={'uuid': cita_uuid['cita_uuid']})


class EliminarConsejeriaPost(EnfermeriaProtectedView, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        consejeria_post = get_object_or_404(ConsejeriaPost, id=kwargs.get('id'))
        consejeria = get_object_or_404(Consejeria, id=consejeria_post.consejeria.id)
        if consejeria:
            ConsejeriaPost.objects.get(id=kwargs.get('id')).delete()
            Consejeria.objects.get(id=consejeria_post.consejeria.id).delete()
            messages.success(self.request, 'Registro eliminado')
        else:
            messages.warning(self.request, 'No existe consejeria registrado para eliminar')
        return reverse(
            'consejeria:crear_consejeria_post',
            kwargs={'uuid': consejeria_post.consejeria.atencion.cita_uuid}
        )
