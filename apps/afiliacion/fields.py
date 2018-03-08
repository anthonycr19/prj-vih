from django.db import models


class PacienteField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 36
        super(PacienteField, self).__init__(*args, **kwargs)
        self.__mpi_data = None
