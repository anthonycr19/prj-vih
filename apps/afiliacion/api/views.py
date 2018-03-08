import logging

import requests

from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from django.shortcuts import render
from apps.common.views import APIProtectedView
from mpi_client.client import MPIClient, CiudadanoClient
from cita_client.client import CITAClient
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib import messages

logger = logging.getLogger(__name__)


class PacienteDataAPIView(APIProtectedView, APIView):
    def get(self, request, *args, **kwargs):
        params = {'dominio': settings.API_CITA_URL, 'uuid': self.kwargs.get('uuid')}
        url = '{dominio}/paciente/buscaruuid/{uuid}'.format(**params)
        r = CITAClient(settings.CITAS_API_TOKEN).get(url=url)
        if r.status_code == 200:
            if len(r.json().get('data')) > 0:
                return Response(r.json())
        return Response({}, status=status.HTTP_404_NOT_FOUND)


def get_cita(uuid):
    data = dict()
    params = {
        'dominio': settings.API_CITA_URL,
        'uuid': uuid,
    }
    url = '{dominio}/citas/get_cita_uuid/{uuid}/'.format(**params)
    try:
        c = CITAClient(settings.CITAS_API_TOKEN).get(url=url)
        if c.status_code == 200:
            data = c.json()
            paciente = data.get('id_phr_paciente', False)
            if paciente:
                data.get('paciente').update(get_ciudadano(paciente))
                url = '{}/servicio/{}/'.format(settings.API_MPI_URL, data.get('cod_ups'))
                u = MPIClient(settings.MPI_API_TOKEN).get(url=url)
                if u.status_code == 200:
                    data.update({'ups': u.json()})
    except Exception as e:
        logger.warning(str(e))
    return data


def get_ciudadano(uuid):
    data = dict()
    try:
        if uuid:
            mpc = MPIClient(settings.MPI_API_TOKEN)
            url = '{}/ciudadano/ver/{}/'.format(settings.API_MPI_URL, uuid)
            m = mpc.get(url=url)
            if m.status_code == 200:
                data = m.json().get('data')
    except Exception as e:
        logger.warning(str(e))
    return data


def actualizar_datos_cnv(datos_actualizar, uuid):
    try:
        ciudadano = CiudadanoClient(settings.MPI_API_TOKEN).actualizar(datos_actualizar, uuid=uuid)

        if ciudadano:
            data_ciudadano = {
                'data': ciudadano,
                'error': 'OK'
            }
        else:
            data_ciudadano = {
                'data': '',
                'error': 'Error al guardar datos en el Servidor de MPI'
            }
    except:
        data_ciudadano = {
            'data': '',
            'error': 'Error de conexión con el Servidor'
        }
    return data_ciudadano


class CiudadanoDataAPIView(APIProtectedView, APIView):
    def get(self, request, *args, **kwargs):
        return Response(get_ciudadano(self.kwargs.get('uuid')))


class CitaListAPIView(APIProtectedView, APIView):
    def get(self, request, *args, **kwargs):
        data = []
        params = {
            'dominio': settings.API_CITA_URL,
            'eess': self.current_establishment,
            'app': settings.APP_IDENTIFIER,
        }
        url = '{dominio}/citas/establecimiento/{eess}/aplicacion/{app}/?'.format(**params)
        if 'fecha' in self.request.GET:
            url = '{}&fecha={}'.format(url, self.request.GET.get('fecha'))
        if 'tipo_doc' in self.request.GET:
            url = '{}&tipo_doc={}'.format(url, self.request.GET.get('tipo_doc'))
        if 'fecha_inicio' in self.request.GET and 'fecha_fin' in self.request.GET:
            url = '{}&fecha_inicio={}&fecha_fin={}'.format(
                url, self.request.GET.get('fecha_inicio'), self.request.GET.get('fecha_fin'))
        try:
            r = CITAClient(settings.CITAS_API_TOKEN).get(url=url)
            if r.status_code == 200:
                data = r.json().get('results')
                if 'ups' in self.request.GET:
                    data = filter(lambda c: c.get('cod_ups', '') in self.request.GET.get('ups', '').split(','), data)
        except Exception as e:
            logger.warning(str(e))
        return Response(data)


class CitaAPIView(APIProtectedView, APIView):
    def get(self, request, *args, **kwargs):
        data = get_cita(self.kwargs.get('uuid'))
        return Response(data)


class CIEListAPIView(APIProtectedView, APIView):
    def get(self, request, *args, **kwargs):
        data = []
        try:
            url = '{}/catalogo/cie/lista/?q={}'.format(settings.API_MPI_URL, self.request.GET.get('q', ''))
            c = MPIClient(settings.MPI_API_TOKEN).get(url=url)
            if c.status_code == 200:
                data = c.json().get('data', [])
        except Exception as e:
            logger.warning(str(e))
        return Response(data)


class CPTListAPIView(APIProtectedView, APIView):
    def get(self, request, *args, **kwargs):
        data = []
        params = {'flag': 'vih', 'dominio': settings.CATALOGO_ODOO_HOST_URL}
        headers = {'Authorization': 'Bearer {}'.format(settings.CATALOGO_ODOO_TOKEN)}
        url = "{dominio}/api/catalogominsa.cpt_procedimiento/?flag={flag}".format(**params)
        try:
            res = requests.get(url=url, headers=headers)
            if res.status_code == 200:
                data = res.json().get('data', [])
        except Exception as e:
            logger.warning(str(e))
        return Response(data)


class InmunicacionAPIView(APIProtectedView, APIView):
    def get(self, request, *args, **kwargs):
        self.vacunas = []
        headers = {
            'Content-Type': 'application/vnd.api+json',
        }
        try:
            dni_paciente = request.GET.get('dni', '')
            response = requests.get(
                '{}/api/v1/vacunaciones/?dni={}'.format(settings.URL_INMUNIZACIONES_SERVER, dni_paciente),
                headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    for d in data['data']:
                        tmp = {
                            'vacuna': d['vacuna'],
                            'fila': d['fila'],
                        }
                        self.vacunas.append(tmp)
                    return self.vacunas
                else:
                    messages.success(self.request, 'No existen vacunas.')
            elif response.status_code == 404:
                messages.warning(self.request, 'Recurso no encontrado')
                print('{} {}'.format(response.url, response.status_code))
            else:
                print('{} {}'.format(response.url, response.status_code))
        except Exception as e:
            logger.warning(str(e))
            messages.warning(self.request, 'Fallo al establecer una conexión al servicio web de MPI')


class DepartamentoView(APIProtectedView, View):
    def get(self, request, *args, **kwargs):
        lista_data = []
        lista_data.append({'codigo': '', 'nombre': '----------'})
        try:
            mpi_client = MPIClient(settings.MPI_API_TOKEN)
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            url = '{}/api/v1/ubigeo/1/177/?page_size=100'.format(settings.MPI_API_HOST)
            response = mpi_client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] or []
                for obj in data:
                    lista_data.append({
                        'codigo': obj['attributes']['cod_ubigeo_inei_departamento'],
                        'nombre': obj['attributes']['ubigeo_departamento']
                    })
            else:
                lista_data = []
        except Exception as e:
            logger.warning(str(e))
            lista_data = []
        return JsonResponse({'data': lista_data})


class ProvinciaView(APIProtectedView, View):
    def get(self, request, *args, **kwargs):
        lista_data = []
        lista_data.append({'codigo': '', 'nombre': '----------'})
        try:
            mpi_client = MPIClient(settings.MPI_API_TOKEN)
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            dep_id = self.kwargs.get('codigo_dep')
            response = mpi_client.get('{}/api/v1/ubigeo/1/177/{}/?page_size=100'.format(settings.MPI_API_HOST, dep_id),
                                      headers=headers)
            if response.status_code == 200:
                data = response.json()['data'] if response.json()['data'] else []
                for obj in data:
                    lista_data.append({
                        'codigo': obj['attributes']['cod_ubigeo_inei_provincia'],
                        'nombre': obj['attributes']['ubigeo_provincia']
                    })
            else:
                lista_data = []
        except Exception as e:
            logger.warning(str(e))
            lista_data = []
        return JsonResponse({'data': lista_data})


class DistritoView(APIProtectedView, View):

    def get(self, request, *args, **kwargs):
        lista_data = []
        lista_data.append({'codigo': '', 'nombre': '----------'})
        try:
            mpi_client = MPIClient(settings.MPI_API_TOKEN)
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            dep_id = self.kwargs.get('codigo_dep')
            prov_id = self.kwargs.get('codigo_pro')
            response = mpi_client.get(
                '{}/api/v1/ubigeo/1/177/{}/{}/?page_size=100'.format(
                    settings.MPI_API_HOST,
                    dep_id,
                    prov_id
                ),
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()['data'] if response.json()['data'] else []
                for obj in data:
                    lista_data.append({
                        'codigo': obj['attributes']['cod_ubigeo_inei_distrito'],
                        'nombre': obj['attributes']['ubigeo_distrito']
                    })
            else:
                lista_data = []
        except Exception as e:
            logger.warning(str(e))
            lista_data = []
        return JsonResponse({'data': lista_data})


class LocalidadView(APIProtectedView, View):

    def get(self, request, *args, **kwargs):
        lista_data = []
        lista_data.append({'codigo': '', 'nombre': '----------'})
        try:
            mpi_client = MPIClient(settings.MPI_API_TOKEN)
            headers = {
                'Content-Type': 'application/vnd.api+json',
            }
            dep_id = self.kwargs.get('codigo_dep')
            prov_id = self.kwargs.get('codigo_pro')
            dist_id = self.kwargs.get('codigo_dis')
            response = mpi_client.get(
                '{}/api/v1/ubigeo/1/177/{}/{}/{}/?page_size=100'.format(
                    settings.MPI_API_HOST,
                    dep_id,
                    prov_id,
                    dist_id
                ),
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()['data'] if response.json()['data'] else []
                for obj in data:
                    lista_data.append({
                        'codigo': obj['attributes']['cod_ubigeo_inei_localidad'],
                        'nombre': obj['attributes']['ubigeo_localidad']
                    })
            else:
                messages.warning(self.request, 'Fallo al establecer una conexión al servicio web de MPI')
        except Exception as e:
            logger.warning(str(e))
            messages.warning(self.request, 'Fallo al establecer una conexión al servicio web de MPI')
        return JsonResponse({'data': lista_data})


def coordenada(request, lat, long):
    data = {
        'lat': lat,
        'long': long
    }
    return render(request, 'paciente/coord_google.html', data)


def consulta_servicio_ciudadano_tipodoc(nro_documento, tipo_documento):
    """
    Consulta a WS de MPI para obtener datos del ciudadano

    :param nro_documento: Numero documento del Ciudadano
    :param tipo_documento: Tipo de documento del Ciudadano
    :return: Diccionario con datos obtenidos de consulta a WS de MPI.
    :rtype: dict
    """

    try:
        ciudadano = CiudadanoClient(settings.MPI_API_TOKEN).ver(nro_documento, tipo_documento)
        if 'error' not in ciudadano.keys():
            data = {
                'uid': ciudadano['uuid'],
                'numero_documento': ciudadano['numero_documento'],
                'tipo_documento': ciudadano['tipo_documento'],
                'nombres': ciudadano.get('nombres', ''),
                'apellido_materno': ciudadano.get('apellido_materno', ''),
                'apellido_paterno': ciudadano.get('apellido_paterno', ''),
                'correo': ciudadano.get('correo', ''),
                'celular': ciudadano.get('celular', ''),
                'sexo': ciudadano.get('sexo', '')
            }
            data_ciudadano = {
                'data': data,
                'error': 'OK'
            }
        else:
            data_ciudadano = {
                'data': '',
                'error': 'Número DNI no encontrado en los Servidores'
            }
    except:
        data_ciudadano = {
            'data': '',
            'error': 'Error en la conexión con el Servidor MPI'
        }
    return data_ciudadano
