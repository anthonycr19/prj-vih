from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import AjaxMedicamentoForm
from .models import Esquema, Medicamento


def medicamento_search(request):
    q = request.GET.get('q', '')
    data = []
    if q:
        for medicamento in Medicamento.objects.filter(Q(descripcion__icontains=q) | Q(codigo__icontains=q)):
            data.append({
                'id': medicamento.id,
                'codigo': medicamento.codigo,
                'descripcion': medicamento.nombre_display,
            })
    return JsonResponse(data, safe=False)


def medicamento_descripcion_search(request):
    q = request.GET.get('q', '')
    data = []
    if q:
        for medicamento in Medicamento.objects.filter(
                        Q(descripcion__icontains=q) | Q(codigo__icontains=q)).distinct('descripcion'):
            data.append({
                'id': medicamento.id,
                'codigo': medicamento.codigo,
                'descripcion': medicamento.descripcion,
            })
    return JsonResponse(data, safe=False)


def esquema_search(request):
    q = request.GET.get('q', '')
    data = []
    if q:
        for esquema in Esquema.objects.filter(Q(descripcion__icontains=q) | Q(tipo__icontains=q)):
            data.append({
                'id': esquema.id,
                'descripcion': esquema.nombre_display,
            })
    return JsonResponse(data, safe=False)


@csrf_exempt
def create_medicamento(request):
    form = AjaxMedicamentoForm(request.POST)
    if form.is_valid():
        medicamento = form.save(commit=False)
        medicamento.targa = True
        medicamento.save()
        return JsonResponse({
            'id': medicamento.id,
            'descripcion': medicamento.descripcion,
            'abreviatura': medicamento.abreviatura
        })
    else:
        return JsonResponse({
            'errors': form.errors
        }, status=400)
