# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-03 21:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('paciente', models.UUIDField(primary_key=True, serialize=False, verbose_name='Paciente')),
            ],
            options={
                'verbose_name_plural': 'Pacientes',
            },
        ),
        migrations.CreateModel(
            name='Poblacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('denominacion', models.CharField(blank=True, max_length=250)),
            ],
            options={
                'verbose_name_plural': 'Poblaciones',
            },
        ),
    ]
