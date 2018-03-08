from datetime import datetime
from dateutil.relativedelta import relativedelta
from mpi_client.client import CiudadanoClient, MPIClient
from django.conf import settings
from apps.afiliacion.models import Paciente


def get_edad_completa_str(fecha_nacimiento):
    try:
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        edad = relativedelta(datetime.now().date(), fecha_nacimiento)
        txt_anios = '{} {}'.format(edad.years or 0, edad.years == 1 and 'año' or 'años')
        txt_meses = '{} {}'.format(edad.months or 0, edad.months == 1 and 'mes' or 'meses')
        txt_dias = '{} {}'.format(edad.days or 0, edad.days == 1 and 'día' or 'días')
        txt_tiempo = '{}, {}, {}.'.format(txt_anios, txt_meses, txt_dias)
        return txt_tiempo
    except:
        return ''


def obtener_establecimiento(codigo):
    headers = {'Content-Type': 'application/vnd.api+json', }
    client = MPIClient(settings.MPI_API_TOKEN)
    response = client.get(
        '{}/api/v1/establecimiento/{}/detalle/'.format(settings.MPI_API_HOST, codigo),
        headers=headers
    )
    establecimiento = []
    if response.status_code == 200:
        data = response.json()['data'] if response.json()['data'] else None
        if data:
            establecimiento = {
                'cod': data['attributes']['codigo_renaes'],
                'desc': data['attributes']['nombre'],
                'cod_disa': data['attributes']['diresa_codigo'],
                'cod_red': data['attributes']['red_codigo'],
                'cod_mred': data['attributes']['microred_codigo'],
                'departamento_nombre': data['attributes']['departamento_nombre'],
                'provincia_nombre': data['attributes']['provincia_nombre'],
                'distrito_nombre': data['attributes']['distrito_nombre'],
                'direccion': data['attributes']['direccion'],
                'ubigeo': data['attributes']['ubigeo'],
                'longitude': data['attributes']['location']['longitude'],
                'latitude': data['attributes']['location']['latitude'],
                'categoria_nombre': data['attributes']['categoria_nombre'],
                'sector_codigo': data['attributes']['sector_codigo'],
                'sector_nombre': data['attributes']['sector_nombre'],
                'diresa_nombre': data['attributes']['diresa_nombre'],
                'red_nombre': data['attributes']['red_nombre'],
                'microred_nombre': data['attributes']['microred_nombre']

            }
            return establecimiento
        else:
            return establecimiento
    else:
        return establecimiento


def consulta_servicio_ciudadano_uuid(uuid):
    try:
        ciudadano = CiudadanoClient(settings.MPI_API_TOKEN).ver(uuid)
        if 'error' not in ciudadano.keys():
            nacimiento = ciudadano['nacimiento_ubigeo']
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
                'paciente': ciudadano['uid'],
                'tipo_documento': ciudadano['tipo_documento'],
                'numero_documento': ciudadano['numero_documento'],
                'apellido_paterno': ciudadano['apellido_paterno'],
                'apellido_materno': ciudadano['apellido_materno'],
                'nombres': ciudadano['nombres'],
                'sexo': ciudadano['sexo'],
                'fecha_nacimiento': ciudadano['fecha_nacimiento'],
                'telefono': ciudadano['telefono'],
                'celular': ciudadano['celular'],
                'correo': ciudadano['correo'],
                'etnia': ciudadano['etnia'],
                'foto': ciudadano['foto'] or '',
                'nacimiento_pais': '177',
                'nacimiento_departamento': dep_nac_inei,
                'nacimiento_provincia': pro_nac_inei,
                'nacimiento_distrito': dis_nac_inei,
                'grado_instruccion': ciudadano['grado_instruccion'],
                'ocupacion': ciudadano['ocupacion'],
                'residencia_actual_pais': '177',
                'residencia_actual_departamento': ciudadano.get('get_departamento_domicilio_ubigeo_inei', ''),  # noqa
                'residencia_actual_provincia': ciudadano.get('get_provincia_domicilio_ubigeo_inei', ''),
                'residencia_actual_distrito': ciudadano.get('get_distrito_domicilio_ubigeo_inei', ''),
                'direccion_actual': ciudadano['domicilio_direccion'] or '',

            }
            Paciente.objects.create(**temp)
            data_ciudadano = {
                'uuid': ciudadano['uid'],
                'resultado': 'OK'
            }
        else:
            data_ciudadano = {
                'uuid': '',
                'resultado': 'Número DNI no encontrado en los Servidores'
            }
    except:
        data_ciudadano = {
            'uuid': '',
            'resultado': 'Actualmente se tiene inconvenientes con la Conexión'
        }
    return data_ciudadano


def consulta_ver_servicio_ciudadano_uuid(uuid):
    try:
        ciudadano = CiudadanoClient(settings.MPI_API_TOKEN).ver(uuid)
        if 'error' not in ciudadano.keys():
            data = {
                'uid': ciudadano['uuid'],
                'numero_documento': ciudadano['numero_documento'],
                'tipo_documento': ciudadano['tipo_documento'],
                'nombres': ciudadano['nombres'],
                'apellido_materno': ciudadano['apellido_materno'],
                'apellido_paterno': ciudadano['apellido_paterno'],
                'correo': ciudadano['correo'],
                'celular': ciudadano['celular'],
                'sexo': ciudadano['sexo'],
                'tipo_seguro': ciudadano['tipo_seguro']
            }
            data_ciudadano = {
                'data': data,
                'resultado': 'OK'
            }
        else:
            data_ciudadano = {
                'data': '',
                'resultado': 'Número DNI no encontrado en los Servidores'
            }
    except Exception as e:
        data_ciudadano = {
            'data': '',
            'resultado': 'Número DNI no encontrado en los Servidores'
        }
    return data_ciudadano


def consulta_servicio_ciudadano_datos_sis_uuid(uuid):
    try:
        datos_ciudadano = consulta_ver_servicio_ciudadano_uuid(uuid)
        if datos_ciudadano['resultado'] == 'OK':
            if datos_ciudadano['data']['tipo_seguro'] == '2':
                ciudadano_sis = CiudadanoClient(settings.MPI_API_TOKEN).ver_datos_sis(uuid)
                eess = obtener_establecimiento(int(ciudadano_sis['codigo_eess']))
                datos_sis = {
                    'codigo_eess': int(ciudadano_sis['codigo_eess']),
                    'nom_eess': eess['desc'],
                    'dir_eess': eess['direccion'],
                    'contrato': ciudadano_sis['contrato'],
                    'tiposeguro': ciudadano_sis['tipo_seguro'],
                    'descripcion_tiposeguro': ciudadano_sis['tipo_seguro_descripcion'],
                    'estadoseguro': ciudadano_sis['estado'],
                    'ubigeo_eess': ciudadano_sis['id_ubigeo'],
                    'regimen': ciudadano_sis['regimen'],
                    'estado': '1'
                }
            else:
                datos_sis = {'estado': '0'}
        else:
            datos_sis = {'estado': '0'}
    except Exception as e:
        datos_sis = {'estado': '2'}
    return datos_sis
