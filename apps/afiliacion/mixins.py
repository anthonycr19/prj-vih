import logging
import traceback
import sys

from django.db import models
from django.conf import settings

from mpi_client.client import MPIClient
from apps.afiliacion.api.views import get_cita, get_ciudadano

logger = logging.getLogger(__name__)

API_VERSION = 'v1'
MPI_API_TOKEN = settings.MPI_API_TOKEN

URL_MPI = '{}/api/{}'.format(settings.MPI_API_HOST, API_VERSION)


class PacienteMixin(models.Model):
    paciente = models.UUIDField(verbose_name='Paciente', db_index=True)

    __mpi_data = None

    class Meta:
        abstract = True

    @property
    def mpi_data(self):
        if self.__mpi_data is None:
            self.__mpi_data = get_ciudadano(self.paciente)
        return self.__mpi_data


class CitaMixin(models.Model):
    cita = models.CharField(verbose_name='Cita', max_length=36, blank=True)

    __cita_data = None

    class Meta:
        abstract = True

    @property
    def cita_data(self):
        if self.__cita_data is None:
            self.__cita_data = get_cita(self.cita)
        return self.__cita_data


class CIEMixin(models.Model):
    cie = models.CharField(max_length=50, blank=True)

    __cie_data = None

    class Meta:
        abstract = True

    @property
    def cie_data(self):
        if self.__cie_data is None:
            try:
                mpi_client = MPIClient(MPI_API_TOKEN)
                r = mpi_client.get('{}/catalogo/cie/detalle/{}/'.format(URL_MPI, self.cie))
                if r.status_code == 200:
                    self.__cie_data = r.json().get('data').get('attributes')
            except Exception as e:
                logger.error('Error obteniendo el cie.')
                logger.error(e.with_traceback(traceback.print_exc(file=sys.stdout)))
        return self.__cie_data


class CPTMixin(models.Model):
    cpt = models.CharField(max_length=50, blank=True)

    __cpt_data = None

    class Meta:
        abstract = True

    @property
    def cpt_data(self):
        if self.__cpt_data is None:
            try:
                mpi_client = MPIClient(MPI_API_TOKEN)
                r = mpi_client.get('{}/catalogo/procedimiento/detalle/{}/'.format(URL_MPI, self.cpt))
                if r.status_code == 200:
                    self.__cpt_data = r.json().get('data').get('attributes')
            except Exception as e:
                logger.error('Error obteniendo datos del CPT.')
                logger.error(e.with_traceback(traceback.print_exc(file=sys.stdout)))
        return self.__cpt_data
