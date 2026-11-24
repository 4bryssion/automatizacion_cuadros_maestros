"""Asistente con Gemini y Confirmar sugerencias del programa (lógica, sin pantalla)."""
import openpyxl
import pytest

from cuadro_maestro import sugerencias as S
from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
from cuadro_maestro.cruce import cruzar
from cuadro_maestro.lectura import leer_carpeta
from muestra_sintetica import NOMBRES, guardar

ADMIN = "administracion-de-empresas"


@pytest.fixture
def config():
    return configuracion_inicial()


def editar(ruta, hoja, cambios):
    wb = openpyxl.load_workbook(ruta)
    ws = wb[hoja] if hoja else wb.worksheets[0]
    for celda, valor in cambios.items():
        ws[celda] = valor
    guardar(wb, ruta)


def leer_y_cruzar(muestra, config):
    lectura = leer_carpeta(muestra, config, 2022, 2022)
    return lectura, cruzar(lectura, config, ADMIN)


@pytest.fixture
def con_problemas(muestra):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"R2": "Univ. Ficticia del Nrte", "C1": "TIPO DE PERSONA"})
    return muestra


def test_preguntas_y_mensaje_sin_datos_de_personas(con_problemas, config):
    lectura, r = leer_y_cruzar(con_problemas, config)
    # Con la columna del vínculo sin identificar la movilidad no se cruza: primero se arregla la columna
    preguntas = S.preguntas_para_gemini(lectura, r, config)
    assert [(p.id, p.tipo, p.como_aparece) for p in preguntas] == [("C1", "columna", "Vínculo")]
    assert "TIPO DE PERSONA" in preguntas[0].opciones and "SEDE (*)" not in preguntas[0].opciones   # ya usada
    config["fuentes"][1]["columnas"]["vinculo"]["elegida"] = "TIPO DE PERSONA"
    lectura, r = leer_y_cruzar(con_problemas, config)
    preguntas = S.preguntas_para_gemini(lectura, r, config)
    assert [(p.id, p.como_aparece) for p in preguntas] == [("I1", "Univ. Ficticia del Nrte")]
    texto = S.mensaje(preguntas)
    assert "I1. Univ. Ficticia del Nrte" in texto and "- UNIVERSIDAD FICTICIA DEL NORTE" in texto
    # Solo nombres de instituciones y títulos: ninguna celda de las filas de movilidad (nombres, documentos…)
    wb = openpyxl.load_workbook(con_problemas / NOMBRES["movilidad"], read_only=True)
    celdas = {str(v) for fila in wb["BD GENERAL"].iter_rows(min_row=2, values_only=True) for v in fila if v}
    instituciones = {p.como_aparece for p in preguntas} | set(preguntas[0].opciones)
    filtradas = {c for c in celdas if c not in instituciones and len(c) > 3 and not c.isdigit()}
    assert not [c for c in filtradas if c in texto]


def test_interpretar_respuestas_de_gemini(config):
    inst = S.Pregunta("I1", S.INSTITUCION, "Univ. Ficticia del Nrte",
                      ["UNIVERSIDAD FICTICIA DEL NORTE", "INSTITUTO DE PRUEBA DEL SUR"])
    otra = S.Pregunta("I2", S.INSTITUCION, "Universidad de Montreal", inst.opciones)
    tercera = S.Pregunta("I3", S.INSTITUCION, "Instituto Sur", inst.opciones)
    col = S.Pregunta("C1", S.COLUMNA, "Vínculo", ["TIPO DE PERSONA", "ROL"], "movilidad", "vinculo")
    sin = S.Pregunta("C2", S.COLUMNA, "Sede", ["X"], "movilidad", "sede")
    texto = """Aquí tienes:
    **I1** → UNIVERSIDAD FICTICIA DEL NORTE
    I2. Universidad de Montreal -> sin coincidencia
    - I3 → Universidad del Sur de Prueba
    C1 → «TIPO DE PERSONA»"""
    r = {x.pregunta.id: x for x in S.interpretar(texto, [inst, otra, tercera, col, sin])}
    assert (r["I1"].estado, r["I1"].propuesta) == (S.POR_CONFIRMAR, "UNIVERSIDAD FICTICIA DEL NORTE")
    assert r["I2"].estado == S.NO_COINCIDE
    assert r["I3"].estado == S.NO_ESTA and not r["I3"].se_puede_guardar          # Gemini inventó un nombre
    assert (r["C1"].estado, r["C1"].propuesta) == (S.POR_CONFIRMAR, "TIPO DE PERSONA")
    assert r["C2"].estado == S.SIN_RESPUESTA
    # Formato del mockup: «1. nombre → OPCIÓN…» (recortada) y sin identificador
    r = S.interpretar("1. Univ. Ficticia del Nrte → UNIVERSIDAD FICTICIA DEL NOR…", [inst])
    assert r[0].propuesta == "UNIVERSIDAD FICTICIA DEL NORTE"
    r = S.interpretar("Univ. Ficticia del Nrte -> universidad ficticia del norte", [inst])
    assert r[0].estado == S.POR_CONFIRMAR
    assert S.lineas_pegadas("a\n\n b \n") == 2
    hecho = S.guardar_respuestas(config, S.interpretar(texto, [inst, otra, tercera, col]))
    assert len(hecho) == 2
    assert config["equivalencias_instituciones"] == [{"como_aparece": "Univ. Ficticia del Nrte",
                                                      "es": "UNIVERSIDAD FICTICIA DEL NORTE", "origen": "gemini"}]
    assert config["fuentes"][1]["columnas"]["vinculo"]["elegida"] == "TIPO DE PERSONA"


def test_confirmar_sugerencias_en_bloque(con_problemas, config):
    config["fuentes"][1]["columnas"]["vinculo"]["elegida"] = "TIPO DE PERSONA"
    editar(con_problemas / NOMBRES["ic1"], None, {"K1": "NOMBRE PROGRAMA, DEPENDENCIA ACADÉMICA"})
    lectura, r = leer_y_cruzar(con_problemas, config)
    sug = S.sugerencias_del_programa(r.avisos, config)
    tipos = {s.tipo: s for s in sug}
    assert set(tipos) == {S.INSTITUCION, S.COLUMNA}
    assert tipos[S.INSTITUCION].propone == "UNIVERSIDAD FICTICIA DEL NORTE" and not tipos[S.INSTITUCION].muy_parecida
    assert tipos[S.COLUMNA].propone == "Programa" and tipos[S.COLUMNA].parecido == 95
    assert not any(s.marcada for s in sug)                                                # ninguna viene marcada
    assert S.marcar_muy_parecidas(sug) == 1 and tipos[S.COLUMNA].marcada
    for s in sug:
        s.marcada = True
    hecho = S.confirmar_marcadas(config, sug)
    assert len(hecho) == 2
    lectura, r = leer_y_cruzar(con_problemas, config)
    assert S.sugerencias_del_programa(r.avisos, config) == []
