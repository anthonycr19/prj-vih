from django.views.generic import TemplateView, ListView, RedirectView
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404

from apps.common.views import EnfermeriaProtectedView
from apps.laboratorio.models import ExamenResultado, Examen

from django.contrib import messages


class LaboratorioExamenIndex(EnfermeriaProtectedView, TemplateView):
    template_name = 'laboratorio/laboratorio_examen_index.html'


class LaboratorioResultadoIndex(EnfermeriaProtectedView, TemplateView):
    template_name = 'laboratorio/laboratorio_resultado_index.html'


def eliminar_examen(request, id):
    if ExamenResultado.objects.filter(laboratorio_examen__id=id).exists():
        datos = {
            'resultado': 'ERROR',
            'detalle': 'No se puede eliminar este Examen tiene un resultado asociado.'
        }
    else:
        try:
            Examen.objects.get(id=id).delete()
            datos = {
                'resultado': 'OK',
                'detalle': 'Registro eliminado satisfactoriamente.'
            }
        except Examen.DoesNotExist:
            datos = {
                'resultado': 'ERROR',
                'detalle': 'No se puede eliminar este Examen, comuníquise con el Administrador.'
            }

    return JsonResponse(datos)


class ListarResultadoExamen(EnfermeriaProtectedView, ListView):
    template_name = 'laboratorio/lista_resultados_examen.html'
    model = ExamenResultado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uuid = self.kwargs.get('uuid', None)
        examenes = Examen.objects.filter(paciente=uuid)
        context.update({
            'examenes': examenes,
        })
        return context


class EliminarResultadoExamen(EnfermeriaProtectedView, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        resultado_examen = get_object_or_404(ExamenResultado, id=kwargs.get('id'))
        if resultado_examen:
            ExamenResultado.objects.get(id=kwargs.get('id')).delete()
            messages.success(self.request, 'Registro eliminado')
        else:
            messages.warning(self.request, 'No existe resultado registrado para eliminar')
        return reverse(
            'laboratorio:listar_resultado_examen',
            kwargs={'uuid': resultado_examen.laboratorio_examen.paciente}
        )
