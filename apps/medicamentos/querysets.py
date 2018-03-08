# coding: utf-8

from django.db import models


class MedicamentoQuerySet(models.QuerySet):

    def targa(self):
        return self.filter(targa=True)
