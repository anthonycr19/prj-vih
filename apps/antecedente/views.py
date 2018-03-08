from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from apps.atencion.models import Atencion
from apps.common.views import MedicoProtectedView
from apps.medicamentos.models import Esquema, EsquemaMedicamento

from .forms import (AntecedentePersonalFormSet, AntecedentesFamiliariesFormSet,
                    AntecedenteTerapiaAntirretroviralForm,
                    AntecedenteTerapiaPreventivaForm,
                    AntecedenteVacunaRecibidaForm)
from .models import (AntecedenteFamiliar, AntecedentePersonal,
                     AntecedenteTerapiaAntirretroviral,
                     AntecedenteTerapiaPreventiva, AntecedenteVacunaRecibida)


class AtencionAntecedenteView(MedicoProtectedView, View):
    template_name = 'atencion/atencion_antecedentes.html'

    def get(self, request, *args, **kwargs):
        tab = request.GET.get('tab') if 'tab' in request.GET.keys() else 'personal'
        atencion = get_object_or_404(Atencion, pk=kwargs.get('pk'))
        historial_personal = AntecedentePersonal.objects.filter(atencion__paciente=kwargs.get('uuid'))
        historial_familiar = AntecedenteFamiliar.objects.filter(atencion__paciente=kwargs.get('uuid'))
        historial_antirretroviral = AntecedenteTerapiaAntirretroviral.objects.filter(
            atencion__paciente=kwargs.get('uuid'))
        historial_preventiva = AntecedenteTerapiaPreventiva.objects.filter(atencion__paciente=kwargs.get('uuid'))
        historial_vacuna = AntecedenteVacunaRecibida.objects.filter(atencion__paciente=kwargs.get('uuid'))
        calendario_inmunizacion = '{}/vacunacion/paciente/{}/mostrar-calendario/'.format(
            settings.URL_INMUNIZACIONES_SERVER, atencion.paciente)
        context = super().get_context_data(**kwargs)
        context.update({
            'tab': tab,
            'object': atencion,
            'historial_personal': historial_personal,
            'historial_familiar': historial_familiar,
            'historial_antirretroviral': historial_antirretroviral,
            'historial_preventiva': historial_preventiva,
            'historial_vacuna': historial_vacuna,
            'calendario_inmunizacion': calendario_inmunizacion,
            'per_forms': AntecedentePersonalFormSet(queryset=AntecedentePersonal.objects.none(), prefix='personal',
                                                    initial=[{'cie': 'B200'}, {'cie': 'B181'}, {'cie': 'I10'},
                                                             {'cie': 'A073'}]),
            'fam_forms': AntecedentesFamiliariesFormSet(queryset=AntecedenteFamiliar.objects.none(), prefix='familiar',
                                                        initial=[{'cie': 'B200'}, {'cie': 'B181'}, {'cie': 'I10'},
                                                                 {'cie': 'A073'}]),
            'art_form': AntecedenteTerapiaAntirretroviralForm(prefix='antirretroviral', initial={'atencion': atencion}),
            'pre_form': AntecedenteTerapiaPreventivaForm(prefix='preventiva', initial={'atencion': atencion}),
            'vac_form': AntecedenteVacunaRecibidaForm(prefix='vacuna', initial={'atencion': atencion}),
        })
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        atencion = get_object_or_404(Atencion, pk=kwargs.get('pk'))
        historial_personal = AntecedentePersonal.objects.filter(atencion__paciente=kwargs.get('uuid'))
        historial_familiar = AntecedenteFamiliar.objects.filter(atencion__paciente=kwargs.get('uuid'))
        historial_antirretroviral = AntecedenteTerapiaAntirretroviral.objects.filter(
            atencion__paciente=kwargs.get('uuid'))
        historial_preventiva = AntecedenteTerapiaPreventiva.objects.filter(atencion__paciente=kwargs.get('uuid'))
        historial_vacuna = AntecedenteVacunaRecibida.objects.filter(atencion__paciente=kwargs.get('uuid'))
        calendario_inmunizacion = '{}/vacunacion/paciente/{}/mostrar-calendario/'.format(
            settings.URL_INMUNIZACIONES_SERVER, atencion.paciente)
        context = super().get_context_data(**kwargs)
        tab = request.POST.get('tab')
        try:
            if tab == 'personal':
                per_forms = AntecedentePersonalFormSet(request.POST, prefix='personal', initial=[
                    {'cie': 'B200'}, {'cie': 'B181'}, {'cie': 'I10'}, {'cie': 'A073'}
                ])
                per_forms.is_valid()
                for obj in per_forms.save(commit=False):
                    obj.atencion = atencion
                    obj.save()
            elif tab == 'familiar':
                fam_forms = AntecedentesFamiliariesFormSet(request.POST, prefix='familiar',
                                                           initial=[{'cie': 'B200'}, {'cie': 'B181'}, {'cie': 'I10'},
                                                                    {'cie': 'A073'}])
                for obj in fam_forms.save(commit=False):
                    obj.atencion = atencion
                    obj.save()
            elif tab == 'antirretroviral':
                url_antirretroviral = '{}?tab={}'.format(atencion.get_atencion_antecedentes_url, tab)
                art_form = AntecedenteTerapiaAntirretroviralForm(request.POST, prefix='antirretroviral')
                if art_form.is_valid():
                    existe_esquema = False
                    art_form.save(commit=False)
                    med1 = art_form.cleaned_data['medicamento1'].id
                    med2 = art_form.cleaned_data['medicamento2'].id
                    med3 = art_form.cleaned_data['medicamento3'].id
                    ver_med4 = art_form.cleaned_data['medicamento4']
                    med4 = ver_med4.id if ver_med4 else 0
                    ver_med5 = art_form.cleaned_data['medicamento5']
                    med5 = ver_med5.id if ver_med5 else 0

                    esquema_medicamento = EsquemaMedicamento.objects.values('esquema_id').filter(
                        medicamento__in=(med1, med2, med3, med4, med5)
                    ).distinct()

                    id_medicamentos_elegidos = []
                    descripcion_med_elegidos = []
                    id_medicamentos_elegidos.append(med1)
                    str_descripcion_med_elegidos = art_form.cleaned_data['medicamento1'].abreviatura
                    id_medicamentos_elegidos.append(med2)
                    str_descripcion_med_elegidos += '/'+art_form.cleaned_data['medicamento2'].abreviatura
                    id_medicamentos_elegidos.append(med3)
                    str_descripcion_med_elegidos += '/'+art_form.cleaned_data['medicamento3'].abreviatura
                    if ver_med4:
                        id_medicamentos_elegidos.append(med4)
                        descripcion_med_elegidos.append(ver_med4.abreviatura)
                        str_descripcion_med_elegidos += '+'+art_form.cleaned_data['medicamento4'].abreviatura
                    if ver_med5:
                        id_medicamentos_elegidos.append(med5)
                        descripcion_med_elegidos.append(ver_med5.abreviatura)
                        str_descripcion_med_elegidos += '+'+art_form.cleaned_data['medicamento5'].abreviatura

                    if esquema_medicamento:
                        id_esquemas_medicamentos = []
                        for row in esquema_medicamento:
                            medicamentos_esquema = Esquema.objects.filter(id=row['esquema_id']).distinct().first()
                            id_esquemas_medicamentos.append({
                                'codigo': medicamentos_esquema.id,
                                'descripcion': medicamentos_esquema.descripcion,
                                'medicamentos': medicamentos_esquema.get_medicamentos
                            })
                        for row in id_esquemas_medicamentos:
                            if med1 and med2 and med3 and ver_med4 and ver_med5:
                                if str(med1) and str(med2) and str(med3) and str(med4) and str(med5) in row['medicamentos']:  # noqa
                                    id_esquema = row
                                    existe_esquema = True
                            elif med1 and med2 and med3 and ver_med4:
                                if str(med1) and str(med2) and str(med3) and str(med4) in row['medicamentos']:
                                    id_esquema = row
                                    existe_esquema = True
                            else:
                                if str(med1) and str(med2) and str(med3) in row['medicamentos']:
                                    id_esquema = row
                                    existe_esquema = True
                        if existe_esquema:
                            id_nuevo_esquema = id_esquema['codigo']
                            descripcion_esquema = id_esquema['descripcion']
                        else:
                            nuevo_esquema = self.guardar_esquema_nuevo(str_descripcion_med_elegidos, art_form)
                            id_nuevo_esquema = nuevo_esquema.id
                            descripcion_esquema = nuevo_esquema.descripcion
                    else:
                        nuevo_esquema = self.guardar_esquema_nuevo(str_descripcion_med_elegidos, art_form)
                        id_nuevo_esquema = nuevo_esquema.id
                        descripcion_esquema = nuevo_esquema.descripcion

                    ant_antirretroviral = AntecedenteTerapiaAntirretroviral(
                        atencion=atencion,
                        medicamento1=art_form.cleaned_data['medicamento1'],
                        medicamento2=art_form.cleaned_data['medicamento2'],
                        medicamento3=art_form.cleaned_data['medicamento3'],
                        medicamento4=art_form.cleaned_data['medicamento4'],
                        medicamento5=art_form.cleaned_data['medicamento5'],
                        fecha_inicio=art_form.cleaned_data['fecha_inicio'],
                        fecha_fin=art_form.cleaned_data['fecha_fin'],
                        obs=art_form.cleaned_data['obs'],
                        esquema=id_nuevo_esquema,
                        descripcion=descripcion_esquema
                    )
                    ant_antirretroviral.save()
                    messages.success(self.request, 'Datos guardados correctamente.')
                    return redirect(url_antirretroviral)
                else:
                    messages.warning(self.request, 'Error en el Formulario verifique los datos ingresados.')
                    context.update({
                        'tab': 'antirretroviral',
                        'object': atencion,
                        'historial_personal': historial_personal,
                        'historial_familiar': historial_familiar,
                        'historial_antirretroviral': historial_antirretroviral,
                        'historial_preventiva': historial_preventiva,
                        'historial_vacuna': historial_vacuna,
                        'calendario_inmunizacion': calendario_inmunizacion,
                        'per_forms': AntecedentePersonalFormSet(
                            queryset=AntecedentePersonal.objects.none(),
                            prefix='personal',
                            initial=[{'cie': 'B200'}, {'cie': 'B181'}, {'cie': 'I10'}, {'cie': 'A073'}]
                        ),
                        'fam_forms': AntecedentesFamiliariesFormSet(
                            queryset=AntecedenteFamiliar.objects.none(),
                            prefix='familiar',
                            initial=[{'cie': 'B200'}, {'cie': 'B181'}, {'cie': 'I10'}, {'cie': 'A073'}]
                        ),
                        'art_form': art_form,
                        'pre_form': AntecedenteTerapiaPreventivaForm(
                            prefix='preventiva',
                            initial={'atencion': atencion}
                        ),
                        'vac_form': AntecedenteVacunaRecibidaForm(prefix='vacuna', initial={'atencion': atencion}),
                    })
                    return render(request, self.template_name, context=context)

            elif tab == 'preventiva':
                pre_form = AntecedenteTerapiaPreventivaForm(request.POST, prefix='preventiva')
                pre_form.save()
            elif tab == 'vacuna':
                vac_form = AntecedenteVacunaRecibidaForm(request.POST, prefix='vacuna')
                vac_form.save()
        except Exception as e:
            messages.warning(self.request, 'Ocurrio un error intentelo nuevamente.')
        url = '{}?tab={}'.format(atencion.get_atencion_antecedentes_url, tab)
        return redirect(url)

    def guardar_esquema_nuevo(self, str_descripcion_med_elegidos, art_form):
        nuevo_esquema = Esquema()
        nuevo_esquema.descripcion = str_descripcion_med_elegidos
        nuevo_esquema.tipo = 'primera_linea'
        nuevo_esquema.etapa_crecimiento = 1
        nuevo_esquema.n_meses = 12
        nuevo_esquema.save()
        nuevo_esquema.medicamentos.add(
            art_form.cleaned_data['medicamento1'],
            art_form.cleaned_data['medicamento2'],
            art_form.cleaned_data['medicamento3']
        )
        if art_form.cleaned_data['medicamento4']:
            nuevo_esquema.medicamentos.add(
                art_form.cleaned_data['medicamento4']
            )
        if art_form.cleaned_data['medicamento5']:
            nuevo_esquema.medicamentos.add(
                art_form.cleaned_data['medicamento5']
            )
        return nuevo_esquema
