import os

import xlsxwriter
from django.conf import settings
from django.db import connection

from apps.afiliacion.models import ATLugarAbordaje
from apps.atencion.models import Atencion
from apps.common.views import get_departamentos, get_provincias, get_distritos
from io import BytesIO


class ReporteUnoExcel(object):
    def __init__(self, departamento, provincia, distrito):
        self.ubigeo_departamento = departamento
        self.ubigeo_provincia = provincia
        self.ubigeo_distrito = distrito

    def get_book(self, output):
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Widen the first column to make the text clearer.
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 21)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 13)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 12)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 13)
        worksheet.set_column('L:L', 13)
        worksheet.set_column('M:O', 11)
        worksheet.set_column('P:R', 11)
        worksheet.set_column('S:S', 16)
        worksheet.set_column('T:T', 14)
        worksheet.set_column('U:AA', 3)
        worksheet.set_column('AB:AB', 14)
        worksheet.set_column('AC:AC', 14)
        worksheet.set_column('AD:AD', 14)
        worksheet.set_column('AE:AE', 14)
        worksheet.set_column('AF:AF', 14)
        worksheet.set_column('AG:AG', 14)
        worksheet.set_column('AH:AH', 14)
        worksheet.set_column('AI:AI', 15)
        worksheet.set_row(1, 25)
        worksheet.set_row(2, 25)
        worksheet.set_row(8, 50)
        worksheet.set_row(9, 37)
        # Add a bold format to use to highlight cells.

        # Write some simple text.
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'blue',
            'font_color': 'white'
        })
        merge_format_purple = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'purple',
            'font_color': 'white'
        })
        merge_format_vertical = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'blue',
            'rotation': 90,
            'font_color': 'white'
        })
        merge_format_title = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font': 15
        })
        merge_format_title_2 = workbook.add_format({
            'bold': 1,
            'valign': 'vcenter',
            'font': 12
        })
        format_resultado = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'white',
            'font_color': 'black'
        })

        filename = os.path.join(settings.BASE_DIR, 'apps/static/minsa_logo.png')
        image_file = open(filename, 'rb')

        image_data = BytesIO(image_file.read())
        image_file.close()
        worksheet.insert_image('A2', filename, {'image_data': image_data, 'x_scale':  0.3,  'y_scale':  0.3})

        worksheet.merge_range('A2:AI2', 'REGISTRO MENSUAL DE BRIGADAS MÓVILES URBANAS Y MCC', merge_format_title)
        worksheet.merge_range('A4:B4', 'A. DIRECCIÓN DE SALUD: ', merge_format_title_2)
        worksheet.merge_range('A5:B5', 'B. RED: ', merge_format_title_2)
        worksheet.merge_range('A6:B6', 'C. MICRORED: ', merge_format_title_2)
        worksheet.merge_range('A7:B7', 'G: ESTRATEGIA DE INTERVENCIÓN: ', merge_format_title_2)
        worksheet.merge_range('E4:F4', 'D. DEPARTAMENTO: ', merge_format_title_2)
        worksheet.merge_range('E5:F5', 'E. PROVINCIA: ', merge_format_title_2)
        worksheet.merge_range('E6:F6', 'F. DISTRITO: ', merge_format_title_2)
        worksheet.merge_range('A9:A10', 'DIRESA/DIRIS', merge_format)
        worksheet.merge_range('B9:B10', 'PROVINCIA', merge_format)
        worksheet.merge_range('C9:C10', 'DISTRITO', merge_format)
        worksheet.merge_range('D9:D10', 'TOTAL\nABORDADOS', merge_format)
        worksheet.merge_range('E9:E10', 'TOTAL\nTAMIZADOS', merge_format)
        worksheet.merge_range('F9:F10', '%\nAbordados /\nTamizados', merge_format_purple)
        worksheet.merge_range('G9:H9', 'ABORDADO\nTIPO DE POBLACIÓN', merge_format)
        worksheet.write('G10', 'HSH', merge_format)
        worksheet.write('H10', 'MT', merge_format)
        worksheet.write('I10', 'HSH', merge_format)
        worksheet.write('J10', 'MT', merge_format)
        worksheet.write('K10', 'HSH', merge_format)
        worksheet.write('L10', 'MT', merge_format)
        worksheet.write('M10', '18-24\nAÑOS', merge_format)
        worksheet.write('N10', '25-54\nAÑOS', merge_format)
        worksheet.write('O10', '55 A MÁS', merge_format)
        worksheet.write('P10', '18-24\nAÑOS', merge_format)
        worksheet.write('Q10', '25-54\nAÑOS', merge_format)
        worksheet.write('R10', '55 A MÁS', merge_format)
        worksheet.merge_range('I9:J9', 'TAMIZADOS\nTIPO DE POBLACIÓN', merge_format)
        worksheet.write('K9', 'Abordado /\nTamizado', merge_format)
        worksheet.write('L9', 'Abordado /\nTamizado', merge_format)
        worksheet.merge_range('M9:O9', 'ABORDADO RANGO DE EDAD', merge_format)
        worksheet.merge_range('P9:R9', 'TAMIZADO RANGO DE EDAD', merge_format)
        worksheet.merge_range('S9:S10', 'CONSEJERÍA PRE\nTEST', merge_format)
        worksheet.merge_range('T9:T10', '%\nTamizado /\nConsejería', merge_format_purple)
        worksheet.merge_range('U9:U10', 'VIH R', merge_format_vertical)
        worksheet.merge_range('V9:V10', 'VIH NR', merge_format_vertical)
        worksheet.merge_range('W9:W10', '% REACTIVOS', merge_format_vertical)
        worksheet.merge_range('X9:X10', 'SIF R', merge_format_vertical)
        worksheet.merge_range('Y9:Y10', 'SIF NR', merge_format_vertical)
        worksheet.merge_range('Z9:Z10', 'HEP R', merge_format_vertical)
        worksheet.merge_range('AA9:AA10', 'HEP R', merge_format_vertical)
        worksheet.merge_range('AB9:AB10', 'CONSEJERÍA\nPOST TEST', merge_format)
        worksheet.merge_range('AC9:AC10', '%\nPre Test /\nPost Test', merge_format)
        worksheet.merge_range('AD9:AD10', 'CONDONES', merge_format)
        worksheet.merge_range('AE9:AE10', 'PROMEDIO\nENTREGADOS', merge_format)
        worksheet.merge_range('AF9:AF10', 'LUBRICANTES', merge_format)
        worksheet.merge_range('AG9:AG10', 'PROMEDIO\nENTREGADOS', merge_format)
        worksheet.merge_range('AH9:AH10', 'VINCULACIÓN\nREFERENCIA\nEESS', merge_format)
        worksheet.merge_range('AI9:AI10', 'APLICACIÓN DE\nFICHA DE\nINFORMACIÓN', merge_format)
        row = 11
        row_two = 11
        inicio = row
        # for ubigeo_dep, nombre in get_departamentos():
        #     inicio = row
        #     for nombre_dep, ubigeo_prov, nombre_prov in get_provincias(ubigeo_dep):
        #         segundo = row_two
        #         for ubigeo_dist, nombre_dist in get_distritos(ubigeo_dep, ubigeo_prov):
        #
        #             worksheet.write('C{}'.format(row), nombre_dist, merge_format)
        #             row = row + 1
        #             row_two = row_two + 1
        #         worksheet.merge_range('B{}:B{}'.format(segundo, row_two-1), nombre_prov, merge_format)
        #     worksheet.merge_range('A{}:A{}'.format(inicio, row-1), nombre, merge_format)

        # for ubigeo_dep, nombre_dep, ubigeo_prov, nombre_prov in get_provincias(14):
        #     segundo = row_two
        #     for ubigeo_dist, nombre_dist in get_distritos(ubigeo_dep, ubigeo_prov):
        #
        #         worksheet.write('C{}'.format(row), nombre_dist, merge_format)
        #         row = row + 1
        #         row_two = row_two + 1
        #     worksheet.merge_range('B{}:B{}'.format(segundo, row_two-1), nombre_prov, merge_format)
        # worksheet.merge_range('A11:A{}'.format(row-1), nombre_dep, merge_format)
        for nombre_dep, nombre_prov, ubigeo_dist, nombre_dist in get_distritos(15, 1506):
            worksheet.write('C{}'.format(row), nombre_dist, merge_format)
            row = row + 1
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                    la.distrito_lugar_abordaje AS distrito, count(ate.id) as total,
                    SUM(CASE
                    WHEN
                    afi.poblacion_id = 2
                    THEN 1 ELSE 0
                    END) AS HSH,
                    SUM(CASE
                    WHEN
                    afi.poblacion_id = 4
                    THEN 1 ELSE 0
                    END) AS MT,
                    SUM(CASE
                    WHEN
                    (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                    AND DATE_PART('year', NOW()::date) - DATE_PART('year', afi.fecha_nacimiento::date) BETWEEN 18 AND 24
                    THEN 1 ELSE 0
                    END) AS edad_18_24,
                    SUM(CASE
                    WHEN
                    (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                    AND DATE_PART('year', NOW()::date) - DATE_PART('year', afi.fecha_nacimiento::date) BETWEEN 25 AND 54
                    THEN 1 ELSE 0
                    END) AS edad_25_54,
                    SUM(
                    CASE
                    WHEN
                    (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                    AND DATE_PART('year', NOW()::date) - DATE_PART('year', afi.fecha_nacimiento::date) BETWEEN 55 AND 120
                    THEN 1 ELSE 0
                    END) AS mayor_55,
                    SUM(CASE
                    WHEN
                    (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                    AND exres.resultado = 'REACTIVO'
                    THEN 1 ELSE 0
                    END) AS reactivo,
                    SUM(CASE
                    WHEN
                    (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                    AND exres.resultado = 'NO REACTIVO'
                    THEN 1 ELSE 0
                    END) AS no_reactivo,
                    SUM(exres.cantidad_condones) as cant_condones,
                    SUM(exres.cantidad_lubricantes) as cant_lubricantes
                    FROM afiliacion_atlugarabordaje AS la
                    INNER JOIN atencion_atencion as ate ON ate.lugar_abordaje_id = la.id
                    INNER JOIN afiliacion_paciente as afi ON ate.paciente_id = afi.paciente
                    INNER JOIN consejeria_consejeria as con ON con.atencion_id= ate.id
                    LEFT JOIN laboratorio_examen as exa ON exa.consejeria_pre_id = con.id
                    LEFT JOIN laboratorio_examenresultado exres ON exres.laboratorio_examen_id = exa.id
                    where la.distrito_lugar_abordaje = %s
                    GROUP BY distrito
                    """, [ubigeo_dist])
                #print(ubigeo_dist)
                resultado = dictfetchall(cursor)
                if not resultado:
                    worksheet.write('D{}'.format(row - 1), '', format_resultado)
                    worksheet.write('G{}'.format(row - 1), '', format_resultado)
                    worksheet.write('H{}'.format(row - 1), '', format_resultado)
                    worksheet.write('M{}'.format(row - 1), '', format_resultado)
                    worksheet.write('N{}'.format(row - 1), '', format_resultado)
                    worksheet.write('O{}'.format(row - 1), '', format_resultado)
                    worksheet.write('U{}'.format(row - 1), '', format_resultado)
                    worksheet.write('V{}'.format(row - 1), '', format_resultado)
                    worksheet.write('AD{}'.format(row - 1), '', format_resultado)
                    worksheet.write('AE{}'.format(row - 1), '', format_resultado)
                    worksheet.write('AF{}'.format(row - 1), '', format_resultado)
                else:
                    print("resultado:", resultado)
                    prom_condones = resultado[0]["cant_condones"]/resultado[0]["total"]
                    worksheet.write('D{}'.format(row - 1), resultado[0]["total"], format_resultado)
                    worksheet.write('G{}'.format(row - 1), resultado[0]["hsh"], format_resultado)
                    worksheet.write('H{}'.format(row - 1), resultado[0]["mt"], format_resultado)
                    worksheet.write('M{}'.format(row - 1), resultado[0]["edad_18_24"], format_resultado)
                    worksheet.write('N{}'.format(row - 1), resultado[0]["edad_25_54"], format_resultado)
                    worksheet.write('O{}'.format(row - 1), resultado[0]["mayor_55"], format_resultado)
                    worksheet.write('U{}'.format(row - 1), resultado[0]["reactivo"], format_resultado)
                    worksheet.write('V{}'.format(row - 1), resultado[0]["no_reactivo"], format_resultado)
                    worksheet.write('AD{}'.format(row - 1), resultado[0]["cant_condones"], format_resultado)
                    worksheet.write('AE{}'.format(row - 1), prom_condones, format_resultado)
                    worksheet.write('AF{}'.format(row - 1), resultado[0]["cant_lubricantes"], format_resultado)
        worksheet.write('C{}'.format(row), 'TOTAL', format_resultado)
        worksheet.merge_range('B11:B{}'.format(row - 1), nombre_prov, merge_format)
        worksheet.merge_range('A11:A{}'.format(row - 1), nombre_dep, merge_format)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                la.distrito_lugar_abordaje AS distrito, count(ate.id) as total,
                SUM(CASE
                WHEN
                afi.poblacion_id = 2
                THEN 1 ELSE 0
                END) AS HSH,
                SUM(CASE
                WHEN
                afi.poblacion_id = 4
                THEN 1 ELSE 0
                END) AS MT,
                SUM(CASE
                WHEN
                (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                AND DATE_PART('year', NOW()::date) - DATE_PART('year', afi.fecha_nacimiento::date) BETWEEN 18 AND 24
                THEN 1 ELSE 0
                END) AS edad_18_24,
                SUM(CASE
                WHEN
                (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                AND DATE_PART('year', NOW()::date) - DATE_PART('year', afi.fecha_nacimiento::date) BETWEEN 25 AND 54
                THEN 1 ELSE 0
                END) AS edad_25_54,
                SUM(
                CASE
                WHEN
                (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                AND DATE_PART('year', NOW()::date) - DATE_PART('year', afi.fecha_nacimiento::date) BETWEEN 55 AND 120
                THEN 1 ELSE 0
                END) AS mayor_55,
                SUM(CASE
                WHEN
                (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                AND exres.resultado = 'REACTIVO'
                THEN 1 ELSE 0
                END) AS reactivo,
                SUM(CASE
                WHEN
                (afi.poblacion_id = 4 OR afi.poblacion_id = 2)
                AND exres.resultado = 'NO REACTIVO'
                THEN 1 ELSE 0
                END) AS no_reactivo,
                SUM(exres.cantidad_condones) as cant_condones,
                SUM(exres.cantidad_lubricantes) as cant_lubricantes
                FROM afiliacion_atlugarabordaje AS la
                INNER JOIN atencion_atencion as ate ON ate.lugar_abordaje_id = la.id
                INNER JOIN afiliacion_paciente as afi ON ate.paciente_id = afi.paciente
                INNER JOIN consejeria_consejeria as con ON con.atencion_id= ate.id
                LEFT JOIN laboratorio_examen as exa ON exa.consejeria_pre_id = con.id
                LEFT JOIN laboratorio_examenresultado exres ON exres.laboratorio_examen_id = exa.id
                where la.distrito_lugar_abordaje = '150606'
                GROUP BY distrito
                """)
            resultado = dictfetchall(cursor)
            #print(resultado[0]["total"])

        workbook.close()

        return workbook


class ReporteDosExcel(object):

    def __init__(self, departamento, provincia, distrito):
        self.ubigeo_departamento = departamento
        self.ubigeo_provincia = provincia
        self.ubigeo_distrito = distrito

    def get_book(self, output):
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Widen the first column to make the text clearer.
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 11)
        worksheet.set_column('C:C', 13)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 13)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 12)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 13)
        worksheet.set_column('L:L', 13)
        worksheet.set_column('M:O', 11)
        worksheet.set_column('P:Q', 11)
        worksheet.set_row(0, 50)
        worksheet.set_row(1, 37)

        # Write some simple text.
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#0099cc',
            'font_color': 'white'
        })
        merge_format_purple = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'purple',
            'font_color': 'white'
        })
        merge_format_vertical = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#0099cc',
            'rotation': 90,
            'font_color': 'white'
        })
        worksheet.merge_range('A1:A2', 'REGIÓN', merge_format)
        worksheet.merge_range('B1:B2', 'PROVINCIA', merge_format)
        worksheet.merge_range('C1:C2', 'LUGAR DE\nABORDAJE', merge_format)
        worksheet.merge_range('D1:D2', 'TOTAL\nABORDADOS', merge_format)
        worksheet.merge_range('E1:E2', 'TOTAL\nTAMIZADOS', merge_format)
        worksheet.merge_range('F1:F2', '%\nAbordados /\nTamizados', merge_format_purple)
        worksheet.merge_range('G1:H1', 'ABORDADO\nTIPO DE POBLACIÓN', merge_format)
        worksheet.write('G2', 'HSH', merge_format)
        worksheet.write('H2', 'MT', merge_format)
        worksheet.write('I2', 'HSH', merge_format)
        worksheet.write('J2', 'MT', merge_format)
        worksheet.write('K2', 'HSH', merge_format)
        worksheet.write('L2', 'MT', merge_format)
        worksheet.merge_range('I1:J1', 'TAMIZADOS\nTIPO DE POBLACIÓN', merge_format)
        worksheet.write('K1', 'Abordado /\nTamizado', merge_format)
        worksheet.write('L1', 'Abordado /\nTamizado', merge_format)
        worksheet.merge_range('M1:M2', 'CONSEJERÍA PRE\nTEST', merge_format)
        worksheet.merge_range('N1:N2', '%\nTamizado /\nConsejería', merge_format_purple)
        worksheet.merge_range('O1:O2', 'VIH R', merge_format_vertical)
        worksheet.merge_range('P1:P2', 'VIH NR', merge_format_vertical)
        worksheet.merge_range('Q1:Q2', '% REACTIVOS', merge_format_vertical)

        row = 2
        for codigo, nombre in get_departamentos():
            row = row + 1
            worksheet.write('A{}'.format(row), nombre, merge_format)
        workbook.close()

        return workbook


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
