import requests
from django.conf import settings
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.authentication import BaseAuthentication


def get_login_host_url():
    return settings.URL_LOGIN_SERVER if not settings.URL_LOGIN_SERVER.endswith('/') else settings.URL_LOGIN_SERVER[:-1]


class APITokenEESSAuthentication(BaseAuthentication):
    auth_roles = ['022']

    def authenticate(self, request):
        """
        Autentica el request con el header X-Login-Token y X-Establecimiento-Id código del establecimiento,
        verifica que el token enviado está activa en el servidor de Logueo,
        verifica que tenga los permisos y roles para realizar alguna operación en el módulo de VIH
        """
        token = request.META.get('HTTP_X_LOGIN_TOKEN')
        if not token:
            raise AuthenticationFailed('Por favor ingrese el token X-Login-Token en el header')
        eess_codigo = request.META.get('HTTP_X_EESS_CODIGO')
        if not eess_codigo:
            raise AuthenticationFailed('Por favor ingrese el X-EESS-Codigo en el header')
        try:
            headers = {'Authorization': 'Token {}'.format(token)}
            data = requests.get('{}/api/v1/permisos/'.format(get_login_host_url()), headers=headers)
        except Exception as e:
            raise AuthenticationFailed('Error al validar los permisos')
        if data.status_code == 200:
            data = data.json()
            if data.get('detail', ''):
                raise AuthenticationFailed('No tiene permisos para acceder a este servicio web')
            permissions = data.get('authorization', {})\
                              .get('permissions', {})\
                              .get('estab:{}'.format(eess_codigo, {}))\
                              .get(settings.APP_IDENTIFIER)
            if permissions:
                roles = []
                x_roles_id = [x[1] for x in permissions.items()]
                for roles_id in x_roles_id:
                    for role_id in roles_id:
                        roles.append(role_id)
                if True in [x in self.auth_roles for x in roles]:
                    # tiene los roles
                    return True, None
                else:
                    PermissionDenied('No tiene los roles necesarios para acceder al módulo de VIH')
            else:
                raise PermissionDenied('No tiene permisos para acceder al módulo de VIH')
        else:
            raise PermissionDenied('No tiene permisos para acceder a este servicio web')


class APITokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        Autentica el request con el header X-Login-Token,
        verifica que el token enviado está activo en el servidor de Logueo
        """
        token = request.META.get('HTTP_X_LOGIN_TOKEN')
        if not token:
            raise AuthenticationFailed('Por favor ingrese el token X-Login-Token en el header')
        try:
            headers = {'Authorization': 'Token {}'.format(token)}
            data = requests.get('{}/api/v1/permisos/'.format(get_login_host_url()), headers=headers)

        except Exception as e:
            raise AuthenticationFailed('Error al validar los permisos')
        if data.status_code == 200:
            data = data.json()
            if data.get('detail', ''):
                raise AuthenticationFailed('No tiene permisos para acceder a este servicio web')
            return data.get('username'), None
        else:
            raise PermissionDenied('No tiene permisos para acceder a este servicio web')
