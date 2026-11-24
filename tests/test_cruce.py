"""Motor de cruce: las 5 reglas, equivalencias, filtros y avisos de la revisión.

La muestra inventada (tests/muestra_sintetica.py) da, para Administración de Empresas en 2022 (calculado a mano):
- UNIVERSIDAD FICTICIA DEL NORTE, específico 2021-2031: Experto internacional 1 (movilidad prefiere el específico).
- UNIVERSIDAD FICTICIA DEL NORTE, marco 2019-2024, VENCIDO: Internacionalización en casa 1 (entra porque tuvo resultados).
- INSTITUTO DE PRUEBA DEL SUR, marco 2020-INDEFINIDO (5 años): Estudiante saliente 1 (no hay específico) e IC 2.
- Universidad Inventada de Ultramar (vencido 2018-2021, sin resultados) queda fuera; ACADEMIA IMAGINARIA no tiene
  fecha de inicio (aviso); CENTRO DE ESTUDIOS FALSOS no aplica al programa.
"""
import openpyxl
import pytest

from conftest import HAY_ANONIMIZADOS, ORIGINALES
from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
from cuadro_maestro.cruce import cruzar, texto_resultados
from cuadro_maestro.cruce import modelos as M
from cuadro_maestro.lectura import leer_carpeta
from muestra_sintetica import NOMBRES, guardar

ADMIN = "administracion-de-empresas"


@pytest.fixture
def config():
    return configuracion_inicial()


def cruce(carpeta, config, programa=ADMIN, desde=2022, hasta=2022):
    return cruzar(leer_carpeta(carpeta, config, desde, hasta), config, programa)


def tabla(r, config):
    return [(f.numero, f.convenio.institucion, f.convenio.tipo, f.convenio.activo,
             texto_resultados(f, config["tipos_persona"])) for f in r.filas]


def tipos(r):
    return sorted(a.tipo for a in r.avisos)


def editar(ruta, hoja, cambios):
    wb = openpyxl.load_workbook(ruta)
    ws = wb[hoja] if hoja else wb.worksheets[0]
    for celda, valor in cambios.items():
        ws[celda] = valor
    guardar(wb, ruta)


# ---------------------------------------------------------------- resultado base
def test_cuadro_de_la_muestra_calculado_a_mano(muestra, config):
    r = cruce(muestra, config)
    assert tabla(r, config) == [
        (1, "INSTITUTO DE PRUEBA DEL SUR", "marco", True,
         "2022\n- Estudiante saliente: 1\n- Internacionalización en casa: 2"),
        (2, "UNIVERSIDAD FICTICIA DEL NORTE", "marco", False, "2022\n- Internacionalización en casa: 1"),
        (3, "UNIVERSIDAD FICTICIA DEL NORTE", "especifico", True, "2022\n- Experto internacional: 1"),
    ]
    assert (r.movilidades_contadas, r.actividades_contadas, r.actividades_sin_institucion) == (2, 3, 2)
    assert r.convenios_del_programa == 5 and not r.sin_convenios
    assert tipos(r) == ["actividades_sin_institucion", "actividades_sin_institucion", "convenio_sin_inicio",
                        "sin_convenio_vigente"]
    sin_inicio = next(a for a in r.avisos if a.tipo == "convenio_sin_inicio")
    assert sin_inicio.grupo == M.EXCEL and "fila 8" in sin_inicio.donde and "Recargar archivos" in sin_inicio.que_hacer
    assert [a.grupo for a in r.avisos] == sorted((a.grupo for a in r.avisos), key=M.ORDEN_GRUPOS.index)


def test_la_vigencia_del_convenio_indefinido_sale_de_inicio_mas_vigencia(muestra, config):
    sur = next(f for f in cruce(muestra, config).filas if f.convenio.institucion.startswith("INSTITUTO"))
    assert (sur.convenio.anio_inicio, sur.convenio.anio_fin, sur.convenio.vigencia_anios) == (2020, 2025, 5)


def test_otro_programa_y_programa_sin_convenios(muestra, config):
    r = cruce(muestra, config, "fisioterapia")
    assert [f.convenio.institucion for f in r.filas] == ["CENTRO DE ESTUDIOS FALSOS"]
    assert texto_resultados(r.filas[0], config["tipos_persona"]) == "Sin evidencia"
    vacio = cruce(muestra, config, "derecho")
    assert vacio.sin_convenios and vacio.convenios_del_programa == 0


# ---------------------------------------------------------------- reglas configurables
def test_regla_1_vencidos_todos(muestra, config):
    config["reglas"]["r1_convenios_que_entran"]["vencidos"] = "todos"
    nombres = [f.convenio.institucion for f in cruce(muestra, config).filas]
    assert "Universidad Inventada de Ultramar" in nombres


def test_regla_2_sin_limite_de_vigencia_asigna_al_convenio_vencido(muestra, config):
    config["reglas"]["r2_asignacion"]["solo_dentro_de_vigencia"] = False
    r = cruce(muestra, config)
    ultramar = next(f for f in r.filas if f.convenio.institucion.startswith("Universidad Inventada"))
    assert ultramar.resultados == {2022: {"Internacionalización en casa": 1}}
    assert "sin_convenio_vigente" not in tipos(r)


def test_regla_2_preferencias_invertidas(muestra, config):
    config["reglas"]["r2_asignacion"].update(preferido_movilidad="marco", preferido_internacionalizacion="especifico")
    norte = {f.convenio.tipo: f.resultados for f in cruce(muestra, config).filas
             if f.convenio.institucion.startswith("UNIVERSIDAD FICTICIA")}
    assert norte["marco"] == {2022: {"Experto internacional": 1}}
    assert norte["especifico"] == {2022: {"Internacionalización en casa": 1}}


def test_regla_2_desempate_por_el_inicio_mas_reciente(muestra, config):
    # Un segundo específico de la misma institución, más reciente, que también cubre 2022.
    editar(muestra / NOMBRES["matriz"], "CONV_INTERNACIONALES",
           {"B10": "UNIVERSIDAD FICTICIA DEL NORTE", "O10": "ESPECÍFICO", "P10": "2022-01-15", "Q10": "2027-01-15",
            "R10": 5, "S10": "VIGENTE", "T10": "APLICA"})
    filas = [f for f in cruce(muestra, config).filas if f.convenio.tipo == "especifico"]
    recibe = {f.convenio.anio_inicio: f.total for f in filas}
    assert recibe == {2021: 0, 2022: 1}


def test_regla_3_una_fila_con_varios_programas(muestra, config):
    # La fila de movilidad 3 lista «Administración de Empresas» y «Contaduría Pública».
    assert cruce(muestra, config, "contaduria-publica").movilidades_contadas == 0     # Contaduría no tiene convenio con SUR
    config["reglas"]["r3_conteo"]["varios_programas_cuentan_para_cada_uno"] = False
    assert cruce(muestra, config).movilidades_contadas == 2                           # Administración va primero
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"J3": "Contaduría Pública\nAdministración de Empresas"})
    assert cruce(muestra, config).movilidades_contadas == 1                           # ya no es el primero


def test_regla_5_estado_no_reconocido_cuenta_como_no_activo(muestra, config):
    editar(muestra / NOMBRES["matriz"], "CONV_INTERNACIONALES", {"S5": "EN TRÁMITE"})
    r = cruce(muestra, config)
    esp = next(f for f in r.filas if f.convenio.tipo == "especifico")
    assert not esp.convenio.activo and "estado_no_reconocido" in tipos(r)
    aviso = next(a for a in r.avisos if a.tipo == "estado_no_reconocido")
    assert "«No Activo»" in aviso.que_paso


@pytest.mark.parametrize("cambios, tipo", [
    ({"Q5": "2020-01-01"}, "convenio_fin_antes_de_inicio"),
    ({"Q6": "INDEFINIDO", "R6": None}, "convenio_sin_fin"),
])
def test_fechas_imposibles_quedan_fuera_con_aviso(muestra, config, cambios, tipo):
    editar(muestra / NOMBRES["matriz"], "CONV_INTERNACIONALES", cambios)
    r = cruce(muestra, config)
    assert tipo in tipos(r)
    assert next(a for a in r.avisos if a.tipo == tipo).grupo == M.EXCEL


# ---------------------------------------------------------------- nombres, equivalencias y tipos
def test_institucion_mal_escrita_se_resuelve_con_una_equivalencia(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"R2": "Univ. Ficticia del Nrte"})
    r = cruce(muestra, config)
    aviso = next(a for a in r.avisos if a.tipo == "institucion_sin_coincidencia")
    assert aviso.grupo == M.PROGRAMA and aviso.titulo == "Institución sin coincidencia: «Univ. Ficticia del Nrte»"
    assert aviso.detalle["sugerencias"][0]["institucion"] == "UNIVERSIDAD FICTICIA DEL NORTE"
    assert M.ELEGIR_INSTITUCION in aviso.acciones and r.movilidades_contadas == 1
    config["equivalencias_instituciones"].append(
        {"como_aparece": "Univ. Ficticia del Nrte", "es": "UNIVERSIDAD FICTICIA DEL NORTE", "origen": "revision"})
    r2 = cruce(muestra, config)
    assert "institucion_sin_coincidencia" not in tipos(r2) and r2.movilidades_contadas == 2


def test_institucion_que_existe_pero_no_aplica_al_programa_es_informativa(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"R2": "Centro de Estudios Falsos"})
    aviso = next(a for a in cruce(muestra, config).avisos if a.tipo == "sin_convenio_del_programa")
    assert aviso.grupo == M.INFORMATIVO and "Administración de Empresas" in aviso.titulo


def test_movilidad_declarada_sin_convenio_es_informativa(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"J5": "Administración de Empresas"})
    aviso = next(a for a in cruce(muestra, config).avisos if a.tipo == "sin_convenio_declarado")
    assert aviso.grupo == M.INFORMATIVO and "Universidad Sin Convenio" in aviso.donde


def test_tipo_de_persona_no_reconocido(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"C2": "Pasante internacional"})
    r = cruce(muestra, config)
    aviso = next(a for a in r.avisos if a.tipo == "tipo_persona_no_reconocido")
    assert aviso.titulo == "Tipo de persona no reconocido: «Pasante internacional»" and M.ABRIR_TIPOS in aviso.acciones
    config["tipos_persona"][2]["valores"].append("pasante internacional")      # Experto internacional
    assert cruce(muestra, config).movilidades_contadas == 2


def test_programa_parecido_se_propone_y_se_resuelve_con_equivalencia(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"J2": "Administracion de Empresa"})
    r = cruce(muestra, config)
    aviso = next(a for a in r.avisos if a.tipo == "programa_parecido")
    assert aviso.detalle == {"como_aparece": "Administracion de Empresa", "es": "Administración de Empresas"}
    assert r.movilidades_contadas == 1
    config["equivalencias_programas"].append(
        {"como_aparece": "Administracion de Empresa", "es": "Administración de Empresas", "origen": "revision"})
    assert cruce(muestra, config).movilidades_contadas == 2


def test_columna_por_confirmar_no_se_usa(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"C1": "VINCULO SNIES DEL PARTICIPANTE"})
    r = cruce(muestra, config)
    assert r.movilidades_contadas == 0
    aviso = next(a for a in r.avisos if a.tipo == "columna_por_confirmar")
    assert aviso.titulo == "Columna por confirmar: «VINCULO SNIES DEL PARTICIPANTE»"
    assert aviso.acciones == [M.CONFIRMAR_SUGERENCIA, M.ABRIR_FUENTES]


def test_filtro_de_sede(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"H4": "Pereira"})   # el docente de Bogotá pasa a Pereira
    assert cruce(muestra, config).movilidades_contadas == 3


# ---------------------------------------------------------------- avisos de la lectura en la revisión
def test_archivos_faltantes_aparecen_en_la_revision_con_sus_textos(muestra, config):
    r = cruce(muestra, config, desde=2021, hasta=2022)
    faltan = [a for a in r.avisos if a.tipo == "falta_archivo"]
    assert [a.titulo for a in faltan] == ["Falta el archivo de Movilidad 2021",
                                          "Falta el archivo de Internacionalización en casa 2021-1",
                                          "Falta el archivo de Internacionalización en casa 2021-2"]
    assert faltan[0].que_paso == "No hay un archivo de movilidad 2021 en la carpeta, así que ese año quedó sin movilidades."
    assert all(a.grupo == M.EXCEL and a.acciones == [M.ABRIR_CARPETA] for a in faltan)


def test_las_claves_de_los_avisos_son_estables_entre_lecturas(muestra, config):
    a = {x.clave for x in cruce(muestra, config, desde=2021).avisos}
    b = {x.clave for x in cruce(muestra, config, desde=2021).avisos}
    assert a == b and len(a) == len(cruce(muestra, config, desde=2021).avisos)


def test_resultados_de_varios_anios_en_orden():
    from cuadro_maestro.cruce.modelos import Convenio, FilaCuadro
    c = Convenio(1, "X", "x", "marco", "MARCO", None, None, None, 2020, 2025, 5, "VIGENTE", True)
    fila = FilaCuadro(1, c, {2025: {"Internacionalización en casa": 1, "Estudiante saliente": 1},
                             2021: {"Internacionalización en casa": 1}, 2024: {"Experto internacional": 1}})
    assert texto_resultados(fila, configuracion_inicial()["tipos_persona"]) == (
        "2021\n- Internacionalización en casa: 1\n2024\n- Experto internacional: 1\n"
        "2025\n- Estudiante saliente: 1\n- Internacionalización en casa: 1")


# ---------------------------------------------------------------- con los Excel reales
@pytest.mark.skipif(not (HAY_ANONIMIZADOS or ORIGINALES), reason="solo con copias anonimizadas u originales")
def test_reproduce_el_cuadro_hecho_a_mano_en_2022(carpeta, config, request):
    if "sintetica" in request.node.callspec.id:
        pytest.skip("la muestra inventada no es el cuadro real")
    r = cruce(carpeta, config)
    con_resultados = {(f.convenio.institucion, f.convenio.tipo, f.convenio.vigencia_anios):
                      f.resultados for f in r.filas if f.total}
    assert con_resultados == {
        ("UNIVERSIDAD CONTINENTAL", "especifico", 10): {2022: {"Experto internacional": 1}},
        ("UNIVERSIDAD CONTINENTAL", "marco", 5): {2022: {"Internacionalización en casa": 10}},
    }
    assert r.actividades_sin_institucion == 3 and r.convenios_del_programa == 157
    revision = {(a.tipo, a.titulo) for a in r.avisos}
    assert ("institucion_sin_coincidencia", "Institución sin coincidencia: «Universidad Siglo 21»") in revision
    assert any(t == "sin_convenio_declarado" for t, _ in revision)
