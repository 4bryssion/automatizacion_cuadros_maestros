"""Motor de lectura: búsqueda por vigencia, errores de apertura, encabezados, columnas y avisos."""
import os
import shutil
import time
from datetime import datetime

import openpyxl
import pytest

from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
from cuadro_maestro.lectura import Cancelado, leer_carpeta
from cuadro_maestro.lectura import libro as L
from cuadro_maestro.lectura import modelos as M
from cuadro_maestro.lectura import valores as V
from muestra_sintetica import NOMBRES, guardar


@pytest.fixture
def config():
    return configuracion_inicial()


def leer(carpeta, config, desde=2022, hasta=2022, **kw):
    return leer_carpeta(carpeta, config, desde, hasta, **kw)


def tipos(lectura):
    return [a.tipo for a in lectura.avisos]


def editar(ruta, hoja, cambios):
    wb = openpyxl.load_workbook(ruta)
    ws = wb[hoja] if hoja else wb.worksheets[0]
    for celda, valor in cambios.items():
        ws[celda] = valor
    guardar(wb, ruta)


# ---------------------------------------------------------------- lectura completa
def test_lee_la_muestra_completa_sin_avisos(muestra, config):
    r = leer(muestra, config)
    assert r.puede_seguir and r.errores == [] and r.avisos == []
    assert [(a.fuente, a.anio, a.semestre, a.fila_encabezados, len(a.registros)) for a in r.archivos] == [
        ("matriz", None, None, 3, 6), ("movilidad", 2022, None, 1, 4),
        ("internacionalizacion_en_casa", 2022, 1, 1, 4), ("internacionalizacion_en_casa", 2022, 2, 2, 3)]
    assert all(a.estado == M.EXACTA for a in r.archivos)
    ic2 = r.archivos[3]
    assert ic2.columnas["anio"].letra == "B"                    # la primera columna es la B
    assert ic2.registros[0].fila == 3                           # número de fila de Excel, para citarlo
    mov = r.archivos[1].registros[1].valores
    assert V.separar_lista(mov["programa"]) == ["Administración de Empresas", "Contaduría Pública"]


def test_la_matriz_trae_la_columna_de_cada_programa(muestra, config):
    m = leer(muestra, config).matriz
    assert len(m.programas) == 25 and {c.estado for c in m.programas.values()} == {M.EXACTA}
    primero = m.registros[0].valores
    assert primero["programas"]["administracion-de-empresas"] == "APLICA"
    assert primero["programas"]["contaduria-publica"] == "NO APLICA"


def test_la_lectura_vale_para_los_tres_juegos_de_archivos(carpeta, config):
    r = leer(carpeta, config)
    assert r.puede_seguir and r.errores == []
    assert [a.fuente for a in r.archivos] == ["matriz", "movilidad", "internacionalizacion_en_casa",
                                             "internacionalizacion_en_casa"]
    assert all(a.estado == M.EXACTA for a in r.archivos)
    assert M.PROGRAMA_NUEVO_EN_MATRIZ not in tipos(r)


# ---------------------------------------------------------------- qué archivos se buscan
def test_vigencia_mas_amplia_avisa_lo_que_falta_sin_bloquear(muestra, config):
    r = leer(muestra, config, 2021, 2023)
    faltan = [(a.fuente, a.anio, a.semestre) for a in r.avisos if a.tipo == M.FALTA_ARCHIVO]
    assert len(faltan) == 6 and ("movilidad", 2021, None) in faltan and ("internacionalizacion_en_casa", 2023, 2) in faltan
    assert r.puede_seguir
    assert sum(e.encontrado for e in r.esperados) == 4 and len(r.esperados) == 10


def test_sin_matriz_no_se_puede_seguir(muestra, config):
    (muestra / NOMBRES["matriz"]).unlink()
    r = leer(muestra, config)
    assert M.FALTA_MATRIZ in tipos(r) and not r.puede_seguir


def test_la_matriz_tambien_se_reconoce_como_convenios_y_no_se_confunde_con_un_cuadro(muestra, config):
    (muestra / NOMBRES["matriz"]).rename(muestra / "Convenios.xlsx")
    shutil.copy(muestra / "Convenios.xlsx", muestra / "CM_20252_Administración_Convenios.xlsx")
    shutil.copy(muestra / "Convenios.xlsx", muestra / "Cuadro maestro - Convenios.xlsx")
    (muestra / "Cuadros generados").mkdir()
    shutil.copy(muestra / "Convenios.xlsx", muestra / "Cuadros generados" / "Matriz de convenios.xlsx")
    r = leer(muestra, config)
    assert r.matriz.ruta.name == "Convenios.xlsx" and M.ARCHIVOS_REPETIDOS not in tipos(r)


def test_dos_archivos_para_el_mismo_anio_usa_el_mas_reciente_y_avisa(muestra, config):
    original = muestra / NOMBRES["movilidad"]
    copia = muestra / "Copia de CONSOLIDADO DE MOVILIDAD INTERNACIONAL 2022 Pereira.xlsm"
    shutil.copy(original, copia)
    antes = time.time() - 3600
    os.utime(original, (antes, antes))
    r = leer(muestra, config)
    mov = next(e for e in r.esperados if e.fuente == "movilidad")
    assert mov.ruta == copia and mov.otros == [original]
    aviso = next(a for a in r.avisos if a.tipo == M.ARCHIVOS_REPETIDOS)
    assert aviso.detalle["descartados"] == [original.name]


def test_archivo_abierto_en_excel_es_solo_informativo(muestra, config):
    (muestra / f"~${NOMBRES['ic1']}").write_bytes(b"\x00" * 165)     # archivo de bloqueo que deja Excel
    r = leer(muestra, config)
    assert tipos(r) == [M.ABIERTO_EN_EXCEL] and r.puede_seguir
    assert len(r.archivos) == 4                                        # el ~$ no se toma como archivo


def test_archivo_sin_semestre_en_el_nombre_se_avisa(muestra, config):
    (muestra / NOMBRES["ic1"]).rename(muestra / "Reporte Internacionalización en casa 2022 Pereira.xlsx")
    r = leer(muestra, config)
    assert M.ARCHIVO_SIN_PERIODO in tipos(r)
    assert sum(1 for a in r.avisos if a.tipo == M.FALTA_ARCHIVO) == 1


# ---------------------------------------------------------------- archivos que no se pueden leer
def test_todos_los_errores_de_lectura_se_recogen_juntos(muestra, config, monkeypatch):
    (muestra / NOMBRES["ic1"]).write_bytes(L.FIRMA_OLE + b"\x00" * 64 + L.MARCA_CIFRADO + b"\x00" * 64)
    (muestra / NOMBRES["ic2"]).write_text("AÑO;SEMESTRE\n2022;2\n", encoding="utf-8")   # un .csv renombrado
    original = L.leer_bytes

    def en_uso(ruta):
        if ruta.name == NOMBRES["movilidad"]:
            raise L.NoSePudoAbrir(M.EN_USO, "simulado")
        return original(ruta)

    monkeypatch.setattr(L, "leer_bytes", en_uso)
    r = leer(muestra, config)
    assert sorted((e.fuente, e.causa) for e in r.errores) == [
        ("internacionalizacion_en_casa", M.CON_CONTRASENA), ("internacionalizacion_en_casa", M.DANADO),
        ("movilidad", M.EN_USO)]
    assert not r.puede_seguir and r.matriz is not None                # lo legible se leyó igual
    err = next(e for e in r.errores if e.causa == M.CON_CONTRASENA)
    assert "contraseña" in err.que_paso and "Reintentar" in err.que_hacer


def test_permiso_denegado_es_archivo_en_uso(muestra, monkeypatch):
    def negar(self):
        raise PermissionError(13, "Permission denied")
    monkeypatch.setattr(type(muestra), "read_bytes", negar)
    with pytest.raises(L.NoSePudoAbrir) as e:
        L.abrir(muestra / NOMBRES["matriz"])
    assert e.value.causa == M.EN_USO


@pytest.mark.parametrize("contenido, detalle", [
    (L.FIRMA_OLE + b"\x00" * 200, "antiguo"),       # un .xls de verdad con extensión .xlsx
    (b"", "No es un libro"),
    (L.FIRMA_ZIP + b"basura", "BadZipFile"),
])
def test_archivos_danados_dan_causa_danado(tmp_path, contenido, detalle):
    ruta = tmp_path / "x.xlsx"
    ruta.write_bytes(contenido)
    with pytest.raises(L.NoSePudoAbrir) as e:
        L.abrir(ruta)
    assert e.value.causa == M.DANADO and detalle in e.value.detalle


# ---------------------------------------------------------------- encabezados y columnas
def test_columna_renombrada_queda_por_confirmar_y_una_desconocida_sin_identificar(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"C1": "VINCULO SNIES DEL PARTICIPANTE", "R1": "Contraparte"})
    r = leer(muestra, config)
    mov = next(a for a in r.archivos if a.fuente == "movilidad")
    assert mov.columnas["vinculo"].estado == M.POR_CONFIRMAR and mov.columnas["vinculo"].letra == "C"
    assert mov.columnas["institucion"].estado == M.SIN_IDENTIFICAR
    assert mov.estado == M.SIN_IDENTIFICAR
    assert {(a.tipo, a.dato) for a in r.avisos} == {(M.COLUMNA_POR_CONFIRMAR, "vinculo"),
                                                    (M.COLUMNA_SIN_IDENTIFICAR, "institucion")}
    assert r.puede_seguir                                       # es un aviso para la revisión, no un error


def test_la_columna_elegida_por_la_persona_cuenta_como_exacta(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"R1": "Contraparte"})
    mov = next(f for f in config["fuentes"] if f["id"] == "movilidad")
    mov["columnas"]["institucion"]["elegida"] = "Contraparte"
    r = leer(muestra, config)
    col = next(a for a in r.archivos if a.fuente == "movilidad").columnas["institucion"]
    assert (col.estado, col.letra) == (M.EXACTA, "R") and r.avisos == []


def test_encabezado_corrido_a_otra_fila_se_detecta(muestra, config):
    wb = openpyxl.load_workbook(muestra / NOMBRES["ic1"])
    wb.worksheets[0].insert_rows(1, 3)
    wb.worksheets[0]["A1"] = "REPORTE DE INTERNACIONALIZACIÓN EN CASA"
    guardar(wb, muestra / NOMBRES["ic1"])
    ic1 = next(a for a in leer(muestra, config).archivos if a.semestre == 1)
    assert ic1.fila_encabezados == 4 and ic1.registros[0].fila == 5 and ic1.estado == M.EXACTA


def test_hoja_sin_encabezados_reconocibles(muestra, config):
    wb = openpyxl.Workbook()
    wb.active.append(["Columna 1", "Columna 2"])
    guardar(wb, muestra / NOMBRES["ic1"])
    r = leer(muestra, config)
    assert M.SIN_ENCABEZADOS in tipos(r)
    ic1 = next(a for a in r.archivos if a.semestre == 1)
    assert ic1.estado == M.SIN_IDENTIFICAR and ic1.registros == []


def test_programa_nuevo_en_la_matriz_y_programa_sin_columna(muestra, config):
    editar(muestra / NOMBRES["matriz"], "CONV_INTERNACIONALES", {"BB3": "Medicina - Pereira", "AC3": "Odontología Pereira X"})
    r = leer(muestra, config)
    nuevos = [a.detalle["encabezado"] for a in r.avisos if a.tipo == M.PROGRAMA_NUEVO_EN_MATRIZ]
    assert nuevos == ["Medicina - Pereira"]
    assert any(a.tipo in (M.PROGRAMA_SIN_COLUMNA, M.COLUMNA_POR_CONFIRMAR) and a.dato == "programa:odontologia"
               for a in r.avisos)


def test_cancelar_detiene_la_lectura(muestra, config):
    vistos = []
    with pytest.raises(Cancelado):
        leer(muestra, config, al_avanzar=lambda fuente, ruta: vistos.append(fuente),
             cancelado=lambda: len(vistos) >= 2)
    assert vistos == ["matriz", "movilidad"]


# ---------------------------------------------------------------- valores
@pytest.mark.parametrize("valor, anio", [(2022, 2022), (2022.0, 2022), ("2022", 2022), (" 2022 ", 2022),
                                         (datetime(2022, 5, 1), 2022), ("dos mil", None), (22, None), (None, None)])
def test_a_anio(valor, anio):
    assert V.a_anio(valor) == anio


@pytest.mark.parametrize("valor, esperado", [("20/05/2022", (2022, 5, 20)), ("2022-05-20", (2022, 5, 20)),
                                             ("20/05/222", None), ("INDEFINIDO", None), ("31/02/2022", None)])
def test_a_fecha(valor, esperado):
    f = V.a_fecha(valor)
    assert (f.year, f.month, f.day) == esperado if esperado else f is None


def test_vacios_y_semestre():
    assert V.es_vacio("N/A") and V.es_vacio(" na ") and V.es_vacio(None) and not V.es_vacio("Universidad X")
    assert V.a_semestre(2.0) == 2 and V.a_semestre("2022-1") == 1 and V.a_semestre(3) is None


def test_un_archivo_sin_cambios_no_se_vuelve_a_abrir(muestra, config, monkeypatch):
    from cuadro_maestro.lectura import lector
    lector.olvidar_leidos()
    primera = leer(muestra, config)
    abiertos = []
    original = lector.abrir
    monkeypatch.setattr(lector, "abrir", lambda ruta: (abiertos.append(ruta), original(ruta))[1])
    segunda = leer(muestra, config)
    assert abiertos == []
    assert [len(a.registros) for a in segunda.archivos] == [len(a.registros) for a in primera.archivos]
    assert len(segunda.avisos) == len(primera.avisos)
    # si cambia la configuración de una fuente, esa fuente se vuelve a leer (y solo esa)
    config["fuentes"][1]["fila_encabezado"] = {"automatica": True, "fila": 1, "x": 1}
    leer(muestra, config)
    assert len(abiertos) >= 1
    # si cambia el archivo, se vuelve a leer
    abiertos.clear()
    ruta = segunda.archivos[0].ruta
    time.sleep(0.01)
    os.utime(ruta, None)
    leer(muestra, config)
    assert ruta in abiertos
