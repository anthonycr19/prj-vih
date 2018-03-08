# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, null=True, verbose_name='Correo electr\xf3nico')),
                ('first_name', models.CharField(max_length=100, verbose_name='First name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Is admin?')),
                ('servicio', models.CharField(blank=True, max_length=24, null=True, verbose_name='Servicios', choices=[('medicina_general', 'Medicina General'), ('infectologia', 'Infectolog\xeda'), ('consejeria', 'Consejer\xeda'), ('enfermeria', 'Enfermer\xeda'), ('laboratorio', 'Laboratorio'), ('psicologia', 'Psicolog\xeda'), ('ginecologia', 'Ginecolog\xeda'), ('asistencia_social', 'Asistencia Social'), ('topico_de_urgencias', 'T\xf3pico de Urgencias')])),
                ('numero_colegiatura', models.CharField(max_length=100, verbose_name='N\xfamero de Colegiatura')),
                ('dni', models.IntegerField(null=True, verbose_name='DNI', blank=True)),
                ('celular', models.IntegerField(null=True, verbose_name='Celular', blank=True)),
                ('username', models.CharField(unique=True, max_length=30, verbose_name='Usuario')),
                ('eess', models.CharField(max_length=10, null=True, verbose_name='C\xf3digo de Establecimiento')),
                ('es_paciente', models.BooleanField(default=False, verbose_name='Es paciente')),
                ('es_recepcion', models.BooleanField(default=False, verbose_name='Es recepcion')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
