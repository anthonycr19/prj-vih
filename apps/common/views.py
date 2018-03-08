import logging
from io import BytesIO

import requests
from cita_client.client import CITAClient
from django.conf import settings
from django.http import HttpResponse
from minsalogin.views import MinsaLoginRequiredView
from mpi_client.client import MPIClient

API_CITA_URL = '{}/api'.format(settings.CITAS_API_HOST)
CITAS_API_TOKEN = settings.CITAS_API_TOKEN

logger = logging.getLogger(__name__)


class EnfermeriaProtectedView(MinsaLoginRequiredView):
    auth_roles = ['005', '006', '025']


class MedicoProtectedView(MinsaLoginRequiredView):
    auth_roles = ['002', '007']


class PsicologiaProtectedView(MinsaLoginRequiredView):
    auth_roles = ['026', ]


class AsistenciaSocialProtectedView(MinsaLoginRequiredView):
    auth_roles = ['027', ]


class LaboratorioProtectedView(MinsaLoginRequiredView):
    auth_roles = ['002', '007', '005', '006', '025', ]


class APIProtectedView(MinsaLoginRequiredView):
    auth_roles = ['002', '007', '005', '006', '025', '005', '006', '026', '027', '072']


class BrigadistaProtectedView(MinsaLoginRequiredView):
    auth_roles = ['071']


class BrigadistaAdminProtectedView(MinsaLoginRequiredView):
    auth_roles = ['072']



class CitaListDataAPIViewMixin(object):
    def get_cita(self, **kwargs):
        r = dict()
        try:
            params = {'dominio': API_CITA_URL, 'eess': self.current_establishment, 'app': settings.APP_IDENTIFIER}
            url = '{dominio}/citas/establecimiento/{eess}/aplicacion/{app}'.format(**params)
            r = CITAClient(CITAS_API_TOKEN).get(url, params=kwargs).json()
        except Exception as e:
            logger.error('Error al obtener las citas programadas.')
            logger.error(e)
        return r


class ExcelView(object):
    """
    Return xlwt WorkBook
    """
    filename = ''

    def render_excel_to_response(self):
        output = BytesIO()
        self.get_book(output)
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename={}'.format(self.filename)
        return response

    def get_book(self, output):
        raise NotImplementedError


class BaseJasperReport(object):
    report_name = ''
    filename = ''

    def __init__(self):
        self.auth = (settings.JASPER_USER, settings.JASPER_PASSWORD)
        super(BaseJasperReport, self).__init__()

    def get_report(self):
        url = '{url}{path}{report_name}.pdf'.format(url=settings.JASPER_URL,
                                                    path=settings.JASPER_PATH,
                                                    report_name=self.report_name)
        req = requests.get(url, params=self.get_params(), auth=self.auth)
        return req.content

    def get_params(self):
        raise NotImplementedError

    def render_to_response(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(self.filename)
        response.write(self.get_report())
        return response


def get_departamentos():
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


def get_provincias(dep_id):
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
                    obj['attributes']['cod_ubigeo_inei_provincia'][0:2],
                    obj['attributes']['ubigeo_departamento'],
                    obj['attributes']['cod_ubigeo_inei_provincia'],
                    obj['attributes']['ubigeo_provincia']
                ))
        else:
            lista_data = []
    except Exception as e:
        lista_data = []
        logger.warning('Error al conectar con MPI', exc_info=True)
    return lista_data


def get_distritos(dep_id, prov_id):
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
                    (
                        obj['attributes']['ubigeo_departamento'],
                        obj['attributes']['ubigeo_provincia'],
                        obj['attributes']['cod_ubigeo_inei_distrito'],
                        obj['attributes']['ubigeo_distrito']
                    )
                )
        else:
            lista_data = []
    except Exception as e:
        lista_data = []
        logger.warning('Error al conectar con MPI', exc_info=True)
    return lista_data
