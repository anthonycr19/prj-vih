# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-06 21:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicamentos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EsquemaMedicamento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'medicamentos_esquema_medicamentos',
                'managed': False,
            },
        ),
    ]