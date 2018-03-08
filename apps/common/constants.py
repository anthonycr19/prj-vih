from apps.common.classes import EnumChoices


class Antecendentes(EnumChoices):
    RSVARON = 'RS con varones'
    RSBI = 'RS con ambos sexos'
    CONTRA = 'Contrasexual'
    DESCONOCIDO = 'Desconocido'


class Transmision(EnumChoices):
    HETERO = 'Heterosexual'
    HOMO = 'Homosexual'
    BI = 'Bisexual'
    NODETERMINADO = 'No determinado'
    TRANSFUSION = 'Transfusión de sangre y/o derivados'
    UDI = 'Compartir agujas/UDI'
    ACCIDENTE = 'Accidente con material contaminado'
    TRANSPLANTE = 'Transplante de órganos ó tejidos'


class Coinfeccion(EnumChoices):
    TB = 0
    HEPATITISB = 1
    HEPATITISC = 2


BOOLEAN_CHOICES = [
    (True, 'Si'),
    (False, 'No')
]
BOOLEAN_CHOICES_NA = (
    (True, u'Si'),
    (False, u'No'),
    (None, u'N/A')
)
ITS_TRATAMIENTO_EN_TRATAMIENTO = 'en_tratamiento'
ITS_TRATAMIENTO_RECIBIO_TRATAMIENTO = 'recibio_tratamiento'
ITS_TRATAMIENTO_NO_RECIBIO_TRATAMIENTO = 'no_recibio_tratamiento'
ITS_TRATAMIENTO_CHOICES = (
    (ITS_TRATAMIENTO_EN_TRATAMIENTO, 'En tratamiento'),
    (ITS_TRATAMIENTO_RECIBIO_TRATAMIENTO, 'Recibió tratamiento'),
    (ITS_TRATAMIENTO_NO_RECIBIO_TRATAMIENTO, 'No recibió tratamiento')
)
CHOICES_POSITIVO = 'positivo'
CHOICES_NEGATIVO = 'negativo'
CHOICES_NO_SABE = 'no_sabe'
CHOICES_POSITIVO_NEGATIVO_NO_SABE = (
    (CHOICES_POSITIVO, 'Positivo'),
    (CHOICES_NEGATIVO, 'Negativo'),
    (CHOICES_NO_SABE, 'No sabe')
)
CHOICES_NUEVO = '1'
CHOICES_CONTINUADOR = '2'
CHOICES_CONDICION_PACIENTE = (
    (CHOICES_POSITIVO, 'Nuevo'),
    (CHOICES_NEGATIVO, 'Continuador'),
)

CHOICES_COMPONENTE = (
    (1, 'c1'),
    (2, 'c2'),
    (3, 'c3'),
)
CULMINACION_CHOICES = (
    (0, '---'),
    (1, 'Aborto'),
    (2, 'Parto Vaginal'),
    (3, 'Cesárea'),
)
MEDICINA_GENERAL = 'medicina_general'
INFECTOLOGIA = 'infectologia'
CONSEJERIA = 'consejeria'
ENFERMERIA = 'enfermeria'
LABORATORIO = 'laboratorio'
PSICOLOGIA = 'psicologia'
GINECOLOGIA = 'ginecologia'
ASISTENCIA_SOCIAL = 'asistencia_social'
TOPICO_DE_URGENCIAS = 'topico_de_urgencias'
CHOICES_SERVICIOS = (
    (MEDICINA_GENERAL, 'Medicina General'),
    (INFECTOLOGIA, 'Infectología'),
    (CONSEJERIA, 'Consejería'),
    (ENFERMERIA, 'Enfermería'),
    (LABORATORIO, 'Laboratorio'),
    (PSICOLOGIA, 'Psicología'),
    (GINECOLOGIA, 'Ginecología'),
    (ASISTENCIA_SOCIAL, 'Asistencia Social'),
    (TOPICO_DE_URGENCIAS, 'Tópico de Urgencias'),
)
SI_NO_CHOICES = ((1, 'SI'), (0, 'NO'))
SI_NO_TEXT_CHOICES = (('1', 'SI'), ('0', 'NO'))
ESTADO_EXAMEN_CHOICES = (
    ('1', 'Solicitado'),
    ('2', 'Con Resultado'),
    ('3', 'Resultado Parcial'),
    ('4', 'Nueva Muestra')
)
DOCUMENTO_DNI = '1'
DOCUMENTO_CE = '2'
DOCUMENTO_PASAPORTE = '3'
DOCUMENTO_CHOICES = (
    (DOCUMENTO_DNI, 'DNI'),
    (DOCUMENTO_PASAPORTE, 'Pasaporte'),
    (DOCUMENTO_CE, 'CE')
)
EC_SOLTER0 = '1'
EC_SEPARADO = '2'
EC_CASADO = '3'
EC_VIUDO = '4'
EC_CONVIVIENTE = '5'
EC_CHOICES = (
    (EC_SOLTER0, 'Soltero(a)'),
    (EC_CASADO, 'Casado(a)'),
    (EC_CONVIVIENTE, 'Conviviente'),
    (EC_SEPARADO, 'Separado(a)'),
    (EC_VIUDO, 'Viudo(a)'),
)

GI_ANALFABETO = '1'
GI_PRIMARIA = '2'
GI_SECUNDARIA = '3'
GI_TECNICO = '4'
GI_SUPERIOR = '5'
GI_CHOICES = (
    (GI_ANALFABETO, 'Analfabeto(a)'),
    (GI_PRIMARIA, 'Primaria'),
    (GI_SECUNDARIA, 'Secundaria'),
    (GI_TECNICO, 'Técnico'),
    (GI_SUPERIOR, 'Superior')
)
GENERO_FEMENINO = '2'
GENERO_MASCULINO = '1'
GENERO_CHOICES = (
    (GENERO_FEMENINO, 'Femenino'),
    (GENERO_MASCULINO, 'Masculino')
)
REFERIDO_LUGAR_CLINICA = 'clinica'
REFERIDO_LUGAR_PARTICULAR = 'medico_particular'
REFERIDO_LUGAR_EESS_MINSA = 'ess_minsa'
REFERIDO_LUGAR_CHOICES = (
    (REFERIDO_LUGAR_CLINICA, 'Clinica'),
    (REFERIDO_LUGAR_PARTICULAR, 'Médico particular'),
    (REFERIDO_LUGAR_EESS_MINSA, 'EESS MINSA')
)
POBLACION_CLAVE_CHOICES = (
    ('1', 'HSH'),
    ('2', 'TRANS'),
    ('3', 'TS-F'),
    ('4', 'TS-HSH'),
    ('5', 'TS-TRANS'),
    ('6', 'Otros'),
)
TIPO_SEGURO_CHOICES = (
    ('1', 'SIS'),
    ('2', 'EsSalud'),
    ('3', 'FFAA'),
    ('4', 'PNP'),
    ('5', 'Privado'),
    ('6', 'SinSeguro'),
    ('7', 'Otro'),
)
TIPO_COMPONENTE_CHOICES = (
    ('1', 'Subsidiado'),
    ('2', 'No Subsidiado'),
)
ESTADO_EXAMEN_FISICO_CHOICES = (
    ('1', 'Conservado'),
    ('2', 'Patologico')
)
ESTADIO_INFEC_CHOICES = (
    ('', '---'),
    ('1', 'Estadío 1'),
    ('2', 'Estadío 2 (Avanzado)'),
    ('3', 'Estadío 3 (SIDA)'),
    ('4', 'Desconocido'),
)
TIPO_DIAGNOSTICO_CHOICES = (
    ('P', 'P'),
    ('D', 'D'),
    ('R', 'R'),
)
ESTADO_COINFECCION_CHOICES = [
    (0, 'No'),
    (1, 'Si')
]
ESTADO_GRAVEDAD_CHOICES = [
    (1, 'Leve'),
    (2, 'Moderado'),
    (3, 'Grave')
]
ATENCION_CONTROL_CHOICES = (
    (1, 'CONTROL por EMD'),
    (2, 'CONTROL LABORATORIO'),
)
EN_CURSO = 'en_curso'
SUSPENDIDO = 'suspendido'
CULMINADO = 'culmiado'
ATENCION_TRATAMIENTO_ESTADO = (
    (EN_CURSO, 'En curso'),
    (SUSPENDIDO, 'Suspendido'),
    (CULMINADO, 'Culminado'),
)
TIPO_DATO_RESULTADO_CHOICES = (
    ('A+', 'A+'),
    ('Indeterminado', 'Indeterminado'),
    ('O+', 'O+'),
    ('VIH-', 'Reactivo(-)'),
    ('VIH+', 'Reactivo(+)'),
)
PRE = 0
POST = 1
TIPO_CONSEJERIA = (
    (PRE, 'Previa'),
    (POST, 'Post')
)
VIA_TRANSMISION = (
    ('sexual', 'Sexual'),
    ('madre_nino', 'Madre Niño'),
    ('parental', 'Parental'),
    ('desconocida', 'Desconocida')
)
DOSIS_CHOICES = ((1, '1'), (2, '2'), (3, '3'),)
RIFAPENTINA_ISONIACIDA = 1
ISONIACIDA_RIFAMPICINA = 2
ISONIACIDA = 3
TERAPIA_PREVENTIVA = (
    (RIFAPENTINA_ISONIACIDA, 'Rifapentina más Isoniacida 1 vez por semana durante 3 meses'),
    (ISONIACIDA_RIFAMPICINA, 'Isoniacida más Rifampicina diario durante 3 meses'),
    (ISONIACIDA, 'Isoniacida diaria durante 9 meses*')
)

REGIMEN_SUBSIDIADO = 1
REGIMEN_SEMICONTRIBUTIVO = 2
REGIMEN_COMPONENTE = 4
REGIMEN_CHOICES = (
    (REGIMEN_SUBSIDIADO, 'Subsidiado'),
    (REGIMEN_SEMICONTRIBUTIVO, 'Semi-Contributivo'),
    (REGIMEN_COMPONENTE, 'Componente SemiSubsidiado'),
)

FINANCIADOR_NO_SE_CONOCE = '0'
FINANCIADOR_USUARIO = '1'
FINANCIADOR_SIS = '2'
FINANCIADOR_ESSALUD = '3'
FINANCIADOR_SOAT = '4'
FINANCIADOR_SANIDAD_FAP = '5'
FINANCIADOR_SANIDAD_NAVAL = '6'
FINANCIADOR_SANIDAD_EP = '7'
FINANCIADOR_SANIDAD_PNP = '8'
FINANCIADOR_PRIVADOS = '9'
FINANCIADOR_OTROS = '10'
FINANCIADOR_EXONERADO = '11'

FINANCIADOR_CHOICES = (
    (FINANCIADOR_NO_SE_CONOCE, 'NO SE CONOCE'),
    (FINANCIADOR_USUARIO, 'USUARIO'),
    (FINANCIADOR_SIS, 'SIS'),
    (FINANCIADOR_ESSALUD, 'ESSALUD'),
    (FINANCIADOR_SOAT, 'S.O.A.T'),
    (FINANCIADOR_SANIDAD_FAP, 'SANIDAD F.A.P'),
    (FINANCIADOR_SANIDAD_NAVAL, 'SANIDAD NAVAL'),
    (FINANCIADOR_SANIDAD_EP, 'SANIDAD EP'),
    (FINANCIADOR_SANIDAD_PNP, 'SANIDAD PNP'),
    (FINANCIADOR_PRIVADOS, 'PRIVADOS'),
    (FINANCIADOR_OTROS, 'OTROS'),
    (FINANCIADOR_EXONERADO, 'EXONERADO'),
)

TIPO_SIN_DOCUMENTO = '00'
TIPO_DOCUMENTO_DNI = '01'
TIPO_DOCUMENTO_LM = '02'
TIPO_DOCUMENTO_CARNET_EXTRANJERIA = '03'
TIPO_DOCUMENTO_ACTA_NACIMIENTO = '04'
TIPO_DOCUMENTO_PASAPORTE = '06'
TIPO_DOCUMENTO_DI_EXTRANJERO = '07'

TDOC_CHOICES = (
    (TIPO_SIN_DOCUMENTO, 'NO SE CONOCE'),
    (TIPO_DOCUMENTO_DNI, 'DNI/LE'),
    (TIPO_DOCUMENTO_LM, 'LM/BO'),
    (TIPO_DOCUMENTO_CARNET_EXTRANJERIA, 'CARNET DE EXTRAJERIA'),
    (TIPO_DOCUMENTO_ACTA_NACIMIENTO, 'ACTA DE NACIMIENTO'),
    (TIPO_DOCUMENTO_PASAPORTE, 'PASAPORTE'),
    (TIPO_DOCUMENTO_DI_EXTRANJERO, 'DI DEL EXTRANJERO'),
)

ETNIA_CHOICES = (
    ('01', 'AYMARA'),
    ('02', 'URO'),
    ('03', 'JAQARU, KAWI (JAQI, CAUQUI)'),
    ('04', 'CHANCAS'),
    ('05', 'CHOPCCAS'),
    ('06', "Q'EROS"),
    ('07', 'WANCAS'),
    ('08', 'OTROS GRUPOS QUECHUAS DEL AREA ANDINA (II)'),
    ('09', 'ACHUAR, ACHUAL'),
    ('10', 'AMAHUACA'),
    ('11', 'AMAIWERI • KISAMBAERI'),
    ('12', 'AMARA KAERI'),
    ('13', 'ANDOA - SHIMIGAE'),
    ('14', 'ANDOKE'),
    ('15', 'ARABELLA (CHIRUPINO)'),
    ('16', 'ARASAIRE'),
    ('17', 'ASHANINKA'),
    ('18', 'ASHENINKA'),
    ('19', 'AWAJUN (AGUARUNA, AENTS)'),
    ('20', 'BORA (MIAMUNA)'),
    ('21', 'CACATAIBO (UNI)'),
    ('22', 'CAHUARANA (MOROCANO)'),
    ('23', 'CANDOSHI - MURATO'),
    ('24', 'CAPANAHUA (JUNIKUIN)'),
    ('25', 'CAQUINTE (POYENISATI)'),
    ('26', 'CASHINAHUA (JUNIKUIN)'),
    ('27', 'CHAMICURO (CHAMEKOLO)'),
    ('28', 'CHITONAHUA'),
    ('29', 'COCAMA - COCAMILLA'),
    ('30', 'CUJARE—O (I—APARI)'),
    ('31', 'CULINA (MADIJA)'),
    ('32', 'ESE´EJA ("H''UARAYO")'),
    ('33', 'HARAKMBUT'),
    ('34', 'HUACHIPAIRE'),
    ('35', 'HUAORANI (TAGAERI, TAROMENANE)'),
    ('36', 'HUITOTO (INCLUYE MURUI, MENECA, MUNAINE)'),
    ('37', 'IQUITO'),
    ('38', 'ISCONAHUA (ICOBAKEBO)'),
    ('39', 'JEBERO (SHIWIIU, SEWELO)'),
    ('40', 'JIBARO'),
    ('41', 'LAMISTO'),
    ('42', 'MACHIGUENGA (MATSIGENKA)'),
    ('43', 'MASHCO - PIRO ("MASHCO")'),
    ('44', 'MASTANAHUA'),
    ('45', 'MAYORUNA (MATS...)'),
    ('46', 'MURUNAHUA'),
    ('47', 'NANTI'),
    ('48', 'NOMATSIGUENGA'),
    ('49', 'OCAINA (IVOT´SA)'),
    ('50', 'OMAGUA'),
    ('51', 'OREJON (MAI HUNA, MAIJUNA)'),
    ('52', 'PISABO (MAYO, KANIBO)'),
    ('53', 'PUKIRIERI'),
    ('54', 'QUICHUA - QUICHUA RUNA, KICHWA (I)'),
    ('55', 'RESIGARO'),
    ('56', 'SAPITERI'),
    ('57', 'SECOYA (AIDO PAI)'),
    ('58', 'CHAPRA'),
    ('59', 'SHARANAHUA / MARINAHUA (ONIKOIN)'),
    ('60', 'SHAWI (CHAYAHUITA, KANPUNAN, KAMPU PIYAWI)'),
    ('61', 'SHIPIBO - CONIBO - SHETEBO'),
    ('62', 'SHUAR'),
    ('63', 'TAUSHIRO (PINCHE)'),
    ('64', 'TICUNA (DU<X<GU)'),
    ('65', 'TOYOERI'),
    ('66', 'URARINA (ITUKALE, SHIMACO, KACH¡)'),
    ('67', 'WAMPIS (HUAMBISA)'),
    ('68', 'YAGUA (YAWA, NIHAMWO)'),
    ('69', 'YAMINAHUA'),
    ('70', 'YANESHA ("AMUESHA")'),
    ('71', 'YINE • YAMI ("PIRO")'),
    ('72', 'YORA ("NAHUA", "PARQUENAHUA")'),
    ('73', 'OTROS GRUPOS INDIGENAS AMAZONICOS'),
    ('80', 'MESTIZO'),
    ('81', 'AFRO DESCENDIENTE'),
    ('82', 'ASIATICO DESCENDIENTE'),
    ('83', 'OTRO')
)

SEXO_CHOICES = (
    ('2', 'Femenino'),
    ('1', 'Masculino')
)

OCUPACION_CHOICES = (
    ('01', 'Profesional'),
    ('02', 'Empleado'),
    ('03', 'Comerciante'),
    ('04', 'Obrero'),
    ('05', 'Ama casa'),
    ('06', 'Estudiante'),
    ('07', 'Sin ocupacion'),
    ('08', 'Otro'),
)

PARENTESCO_CHOICES = (
    ('1', 'Padre'),
    ('2', 'Madre'),
    ('3', 'Hijo'),
    ('4', 'Hija'),
    ('5', 'Esposo'),
    ('6', 'Esposa'),
)

GI_CHOICES = (
    ('00', 'Sin instrucción'),
    ('01', 'Educación inicial'),
    ('02', 'Primaria completa'),
    ('03', 'Primaria incompleta'),
    ('04', 'Educación especial'),
    ('05', 'Secundaria completa'),
    ('06', 'Secundaria cncompleta'),
    ('07', 'Superior técnica completa'),
    ('08', 'Superior técnica incompleta'),
    ('09', 'Superior universitaria completa'),
    ('10', 'Superior universitaria incompleta'),
    ('11', 'Sin información'),
    ('12', 'No corresponde (menores de 3 años)'),
)


ESTADO_CITA_PENDIENTE = 1
ESTADO_CITA_CONFIRMADO = 2
ESTADO_CITA_ATENDIDO = 3
ESTADO_CITA_CANCELADO = 4
ESTADO_CITA_FINALIZADO = 5
ESTADO_CITA_AUSENTE = 6
ESTADO_CITA_REPROGRAMADO = 7

ESTADO_CITA_CHOICES = (
    (ESTADO_CITA_PENDIENTE, 'Pendiente'),
    (ESTADO_CITA_CONFIRMADO, 'Confirmada'),
    (ESTADO_CITA_ATENDIDO, 'Atendido'),
    (ESTADO_CITA_CANCELADO, 'Cancelado'),
    (ESTADO_CITA_FINALIZADO, 'Finalizado'),
    (ESTADO_CITA_AUSENTE, 'Ausente'),
    (ESTADO_CITA_REPROGRAMADO, 'Reprogramado')
)

ESTADO_ATENCION_PENDIENTE = 1
ESTADO_ATENCION_ATENDIDO = 2
ESTADO_ATENCION_AUSENTE = 3

ESTADO_ATENCION_CHOICES = (
    (ESTADO_ATENCION_PENDIENTE, 'Pendiente'),
    (ESTADO_ATENCION_ATENDIDO, 'Atendido'),
    (ESTADO_ATENCION_AUSENTE, 'Ausente'),
)

TIPO_ATENCION_CITA = 1
TIPO_ATENCION_DEMANDA = 2

TIPO_ATENCION_CHOICES = (
    (TIPO_ATENCION_CITA, 'Cita'),
    (TIPO_ATENCION_DEMANDA, 'Demanda'),
)

TAMIZAJE_WEB = 'WEB'
TAMIZAJE_MOVIL = 'MOVIL'

PACIENTE_VIH = (
    (TAMIZAJE_WEB, 'VIH'),
    (TAMIZAJE_MOVIL, 'APP_VIH'),
)

ID_PAIS_PERU = 177

LUGAR_ABORDAJE_OTRO = 'Otro'

RESULTADO_EXAMEN_REACTIVO = 'REACTIVO'
RESULTADO_EXAMEN_NO_REACTIVO = 'NO REACTIVO'
RESULTADO_EXAMEN_INDETERMINADO = 'INDETERMINADO'

RESULTADO_EXAMEN = (
    (RESULTADO_EXAMEN_REACTIVO, 'Reactivo'),
    (RESULTADO_EXAMEN_NO_REACTIVO, 'No Reactivo'),
    (RESULTADO_EXAMEN_INDETERMINADO, 'Indeterminado'),
)

ESTADO_SERVICIO_SIS_ERROR = '2'
ESTADO_SERVICIO_SIS_TIENE_SIS = '1'
ESTADO_SERVICIO_SIS_NO_TIENE_SIS = '0'

ESTADO_SERVICIO_SIS = (
    (ESTADO_SERVICIO_SIS_ERROR, 'Error al conectarse al SIS'),
    (ESTADO_SERVICIO_SIS_TIENE_SIS, 'Tiene SIS'),
    (ESTADO_SERVICIO_SIS_NO_TIENE_SIS, 'No tiene SIS'),
)

TIPO_EGRESO_ABANDONO = 1
TIPO_EGRESO_DERIVACION = 2
TIPO_EGRESO_FALLECIMIENTO = 3

TIPO_EGRESO_CHOICES = (
    (TIPO_EGRESO_ABANDONO, 'Abandono'),
    (TIPO_EGRESO_DERIVACION, 'Derivación'),
    (TIPO_EGRESO_FALLECIMIENTO, 'Fallecimiento'),
)

EGRESO_PRIMER_EPISODIO = 1
EGRESO_SEGUNDO_EPISODIO = 2
EGRESO_TERCER_EPISODIO = 3

EGRESO_EPISODIO_CHOICES = (
    (EGRESO_PRIMER_EPISODIO, '1er episodio'),
    (EGRESO_SEGUNDO_EPISODIO, '2do episodio'),
    (EGRESO_TERCER_EPISODIO, '3er episodio'),
)

EGRESO_LUGAR_FALLECIMIENTO_EESS = 1
EGRESO_LUGAR_FALLECIMIENTO_OTRO_EESS = 2
EGRESO_LUGAR_FALLECIMIENTO_DOMICILIO = 3
EGRESO_LUGAR_FALLECIMIENTO_OTRO = 4

EGRESO_LUGAR_FALLECIMIENTO_CHOICES = (
    (EGRESO_LUGAR_FALLECIMIENTO_EESS, 'En el EESS'),
    (EGRESO_LUGAR_FALLECIMIENTO_OTRO_EESS, 'Otro EESS'),
    (EGRESO_LUGAR_FALLECIMIENTO_DOMICILIO, 'En el domicilio'),
    (EGRESO_LUGAR_FALLECIMIENTO_OTRO, 'Otro'),
)
