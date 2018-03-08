# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext as _

from django.db import models
from apps.common import constants

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    REQUIRED_FIELDS = ('first_name', 'last_name')
    USERNAME_FIELD = 'username'

    email = models.EmailField(_('Email'), unique=True, null=True)
    first_name = models.CharField(_('First name'), max_length=100)
    last_name = models.CharField(_('Last name'), max_length=100)
    is_active = models.BooleanField(_('Is active?'), default=True)
    is_admin = models.BooleanField(_('Is admin?'), default=False)
    servicio = models.CharField(_('Servicios'), max_length=24, choices=constants.CHOICES_SERVICIOS, blank=True,
                                null=True)
    numero_colegiatura = models.CharField(_('Número de Colegiatura'), max_length=100)
    dni = models.IntegerField(_('DNI'), blank=True, null=True)
    celular = models.IntegerField(_('Celular'), blank=True, null=True)
    username = models.CharField('Usuario', unique=True, max_length=30)
    eess = models.CharField(max_length=10, verbose_name='Código de Establecimiento', null=True)
    es_paciente = models.BooleanField('Es paciente', default=False)
    es_recepcion = models.BooleanField('Es recepcion', default=False)

    objects = UserManager()

    created = models.DateTimeField(auto_now_add=True, editable=True)
    modified = models.DateTimeField(auto_now=True, editable=True)

    @property
    def is_staff(self):
        return self.is_admin

    def get_full_name(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.username

    def __str__(self):
        return u'{} {}'.format(self.first_name, self.last_name)
