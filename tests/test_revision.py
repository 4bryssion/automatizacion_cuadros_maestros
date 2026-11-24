"""Lógica de Ver revisión: recargar, comparar, cambios sin incluir y resolver dentro del programa."""
import copy

import openpyxl
import pytest

from cuadro_maestro import revision as RV
from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
from cuadro_maestro.cruce import cruzar
from cuadro_maestro.lectura import leer_carpeta
from muestra_sintetica import NOMBRES, guardar

ADMIN = "administracion-de-empresas"


@pytest.fixture
def config():
    return configuracion_inicial()


@pytest.fixture
def generado(muestra, config):
    """Lo que se guarda al generar: avisos, huellas de filas y de configuración."""
    r = cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    return r.avisos, RV.firmas_filas(r, config), RV.firmas_config(config)


def recargar(muestra, config, generado):
    avisos, firmas, cfg = generado
    return RV.recargar(muestra, config, ADMIN, 2022, 2022, avisos, firmas, cfg)


def editar(ruta, hoja, cambios):
    wb = openpyxl.load_workbook(ruta)
    ws = wb[hoja]
    for celda, valor in cambios.items():
        ws[celda] = valor
    guardar(wb, ruta)


def test_recargar_sin_cambios(muestra, config, generado):
    r = recargar(muestra, config, generado)
    assert (len(r.comparacion.resueltos), len(r.comparacion.nuevos), len(r.comparacion.siguen)) == (0, 0, 4)
    assert not r.hay_cambios and (r.leidos, r.esperados) == (3, 3)


def test_guardar_un_excel_sin_cambiar_nada_no_cuenta(muestra, config, generado):
    ruta = muestra / NOMBRES["movilidad"]
    guardar(openpyxl.load_workbook(ruta), ruta)
    assert not recargar(muestra, config, generado).hay_cambios


def test_un_cambio_en_el_excel_da_aviso_nuevo_y_filas_que_cambian(muestra, config, generado):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"R2": "Univ. Ficticia del Nrte"})
    r = recargar(muestra, config, generado)
    assert [a.tipo for a in r.comparacion.nuevos] == ["institucion_sin_coincidencia"]
    assert r.filas_cambian == 1 and r.hay_cambios and r.comparacion.ahora == 5


def test_corregir_en_el_excel_resuelve_el_aviso(muestra, config, generado):
    editar(muestra / NOMBRES["matriz"], "CONV_INTERNACIONALES", {"P8": "2020-03-15"})     # ACADEMIA ya tiene fecha
    r = recargar(muestra, config, generado)
    assert [a.tipo for a in r.comparacion.resueltos] == ["convenio_sin_inicio"]
    assert RV.que_se_logro(r.comparacion.resueltos[0]) == "ya tiene fecha, vuelve a contar en el cuadro"
    assert r.filas_cambian == 0 and not r.hay_cambios        # la Academia no aplica a ningún resultado: igual queda fuera


def test_equivalencia_desde_la_revision_resuelve_y_cuenta_como_cambio_de_configuracion(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"R2": "Univ. Ficticia del Nrte"})
    r0 = cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    generado = (r0.avisos, RV.firmas_filas(r0, config), RV.firmas_config(config))
    aviso = next(a for a in r0.avisos if a.tipo == "institucion_sin_coincidencia")
    nueva = RV.guardar_equivalencia_institucion(copy.deepcopy(config), aviso.detalle["como_aparece"],
                                                aviso.detalle["sugerencias"][0]["institucion"])
    assert nueva["equivalencias_instituciones"][-1]["origen"] == "revision"
    r = recargar(muestra, nueva, generado)
    assert [a.tipo for a in r.comparacion.resueltos] == ["institucion_sin_coincidencia"]
    assert r.filas_cambian == 1 and r.config_cambiada == {"Equivalencias de instituciones": 1}


def test_confirmar_sugerencia_de_columna_y_de_programa(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"C1": "VINCULO SNIES DEL PARTICIPANTE",
                                                          "J3": "Administracion de Empresa"})
    r = cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    assert r.movilidades_contadas == 0
    columna = next(a for a in r.avisos if a.tipo == "columna_por_confirmar")
    assert "Fuentes de datos" in RV.confirmar_sugerencia(config, columna)
    r = cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    assert r.movilidades_contadas == 1
    programa = next(a for a in r.avisos if a.tipo == "programa_parecido")
    assert "Equivalencias de programas" in RV.confirmar_sugerencia(config, programa)
    assert cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN).movilidades_contadas == 2


def test_los_avisos_se_guardan_y_se_recuperan_iguales(generado):
    avisos = generado[0]
    assert [RV.aviso_de_dict(RV.aviso_a_dict(a)) for a in avisos] == avisos


def test_instituciones_de_la_matriz(muestra, config):
    inst = dict(RV.instituciones_de_la_matriz(muestra, config))
    assert inst["UNIVERSIDAD FICTICIA DEL NORTE"] == 2 and len(inst) == 5


def test_filas_que_cambian():
    assert RV.filas_que_cambian(["a", "b", "c"], ["a", "b", "c"]) == 0
    assert RV.filas_que_cambian(["a", "b", "c"], ["a", "x", "c"]) == 1
    assert RV.filas_que_cambian(["a", "b"], ["a", "b", "c", "d"]) == 2
