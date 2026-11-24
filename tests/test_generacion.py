"""Generación del cuadro: formato del Excel, nombre, errores que la detienen y cancelación."""
import errno
import zipfile
from datetime import datetime

import openpyxl
import pytest

from conftest import HAY_ANONIMIZADOS, ORIGINALES
from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
from cuadro_maestro.generacion import (CARPETA_SALIDA, Cancelado, GeneracionDetenida, detalle_para_sistemas, generar,
                                       nombre_cuadro)
from cuadro_maestro.generacion import escritor as W
from cuadro_maestro.generacion import proceso as P
from cuadro_maestro.generacion.nombre import ruta_libre
from cuadro_maestro.lectura import libro as L
from cuadro_maestro.lectura import modelos as LM
from muestra_sintetica import NOMBRES

ADMIN = "administracion-de-empresas"
AHORA = datetime(2026, 11, 24, 14, 32)


@pytest.fixture
def config():
    return configuracion_inicial()


def gen(carpeta, config, programa=ADMIN, desde=2022, hasta=2022, **kw):
    kw.setdefault("logo", None)
    return generar(carpeta, config, programa, desde, hasta, ahora=kw.pop("ahora", AHORA), **kw)


def salida(carpeta):
    d = carpeta / CARPETA_SALIDA
    return sorted(p.name for p in d.iterdir()) if d.exists() else []


# ---------------------------------------------------------------- el Excel
def test_el_cuadro_tiene_el_formato_del_hecho_a_mano(muestra, config, monkeypatch):
    monkeypatch.setattr(P, "logo_cna", lambda: None)
    g = gen(muestra, config)
    assert g.ruta.name == "Cuadro maestro - Administración de Empresas - 2022 - 2026-11-24 1432.xlsx"
    assert salida(muestra) == [g.ruta.name]                     # sin temporales
    wb = openpyxl.load_workbook(g.ruta)
    ws = wb["Convenios"]
    assert [ws[f"A{i}"].value for i in (1, 2, 3)] == list(W.TITULOS)
    assert ws["A5"].value == W.TITULO_NACIONALES and ws["A16"].value == W.TITULO_INTERNACIONALES
    assert [ws.cell(r, 1).value for r in range(7, 14)] == list(W.FILAS_EJEMPLO_NACIONALES)
    assert [c.value for c in ws[17]] == [c["nombre"] for c in config["campos"]]
    filas = [[c.value for c in ws[r]] for r in (18, 19, 20)]
    assert filas == [
        [1, "INSTITUTO DE PRUEBA DEL SUR", "Objeto ficticio del convenio 3",
         "2022\n- Estudiante saliente: 1\n- Internacionalización en casa: 2", 5, "Activo", None, None],
        [2, "UNIVERSIDAD FICTICIA DEL NORTE", "Objeto ficticio del convenio 1",
         "2022\n- Internacionalización en casa: 1", 5, "No Activo", None, None],
        [3, "UNIVERSIDAD FICTICIA DEL NORTE", "Objeto ficticio del convenio 2",
         "2022\n- Experto internacional: 1", 10, "Activo", None, None],
    ]
    assert ws.max_row == 20
    assert {"A1:H1", "A5:H5", "A16:H16"} <= {str(r) for r in ws.merged_cells.ranges}
    a18, h20 = ws["A18"], ws["H20"]
    assert a18.font.name == "Century Gothic" and a18.font.sz == 10 and a18.alignment.wrap_text
    assert a18.border.left.style == "medium" and h20.border.right.style == "medium" and h20.border.bottom.style == "medium"
    assert ws["B18"].border.left.style == "thin" and ws["E18"].number_format == "0"
    assert ws.column_dimensions["C"].width == 64.5 and ws.row_dimensions[18].height >= 25
    acerca = {wb["Acerca de este cuadro"].cell(r, 1).value: wb["Acerca de este cuadro"].cell(r, 2).value
              for r in range(3, 17)}
    assert acerca["Programa"] == "Administración de Empresas" and acerca["Convenios en el cuadro"] == 3
    assert acerca["Movilidades contadas"] == 2 and acerca["Generado el"] == "24/11/2026 14:32"


def test_las_columnas_salen_de_campos_del_cuadro(muestra, config):
    campos = config["campos"]
    campos[:] = [c for c in campos if c["id"] != "no_aplica"]
    campos.insert(2, {"id": "codigo", "nombre": "Código", "fuente": "matriz", "dato": "codigo", "tipo": "texto",
                      "base": False, "ancho": 14})
    campos[1]["nombre"] = "Institución"
    ws = openpyxl.load_workbook(gen(muestra, config).ruta)["Convenios"]
    assert [c.value for c in ws[17]][:4] == ["No.", "Institución", "Código", "Breve Objeto"]
    assert ws["C18"].value == "FUAA-1003" and ws.max_column == 8
    assert "A16:H16" in {str(r) for r in ws.merged_cells.ranges}


def test_con_logo(muestra, config, tmp_path):
    from PIL import Image
    logo = tmp_path / "logo.png"
    Image.new("RGB", (40, 20), "white").save(logo)
    with zipfile.ZipFile(gen(muestra, config, logo=logo).ruta) as z:
        assert any(n.startswith("xl/media/") for n in z.namelist())


# ---------------------------------------------------------------- nombre
def test_nombre_del_cuadro():
    assert nombre_cuadro("Fisioterapia", 2019, 2023, AHORA) == "Cuadro maestro - Fisioterapia - 2019-2023 - 2026-11-24 1432.xlsx"
    assert nombre_cuadro('Diseño: "Modas"/Textil.', 2022, 2022, AHORA) == "Cuadro maestro - Diseño Modas Textil - 2022 - 2026-11-24 1432.xlsx"


def test_el_mismo_minuto_lleva_2_y_3(muestra, config):
    nombres = [gen(muestra, config).ruta.name for _ in range(3)]
    assert nombres == ["Cuadro maestro - Administración de Empresas - 2022 - 2026-11-24 1432.xlsx",
                       "Cuadro maestro - Administración de Empresas - 2022 - 2026-11-24 1432 (2).xlsx",
                       "Cuadro maestro - Administración de Empresas - 2022 - 2026-11-24 1432 (3).xlsx"]


def test_ruta_libre_no_pisa_archivos(tmp_path):
    (tmp_path / "a.xlsx").write_text("")
    (tmp_path / "a (2).xlsx").write_text("")
    assert ruta_libre(tmp_path, "a.xlsx").name == "a (3).xlsx"


# ---------------------------------------------------------------- pasos y avance
def test_avance_por_los_cinco_pasos(muestra, config):
    eventos = []
    g = gen(muestra, config, desde=2021, al_avanzar=lambda p, e, t: eventos.append((p, e)))
    assert [p for p, e in eventos if e == P.EN_CURSO] == ["matriz", "movilidad", "ic", "cruce", "escritura"]
    estados = {p.paso: (p.estado, p.texto) for p in g.pasos}
    assert estados["movilidad"] == (P.CON_AVISO, "falta 2021")
    assert estados["ic"] == (P.CON_AVISO, "falta 2021-1, 2021-2")
    assert estados["escritura"][0] == P.HECHO and estados["cruce"] == (P.HECHO, "3 convenios")


# ---------------------------------------------------------------- se detiene
def test_errores_de_lectura_detienen_sin_crear_archivo(muestra, config, monkeypatch):
    (muestra / NOMBRES["ic1"]).write_bytes(L.FIRMA_OLE + b"\x00" * 64 + L.MARCA_CIFRADO)
    original = L.leer_bytes
    monkeypatch.setattr(L, "leer_bytes", lambda r: (_ for _ in ()).throw(L.NoSePudoAbrir(LM.EN_USO))
                        if r.name == NOMBRES["movilidad"] else original(r))
    with pytest.raises(GeneracionDetenida) as e:
        gen(muestra, config)
    err = e.value
    assert [(x.paso, x.etiqueta) for x in err.errores] == [("movilidad", "Archivo en uso"), ("ic", "Con contraseña")]
    assert {p.paso: p.estado for p in err.pasos} == {"matriz": P.HECHO, "movilidad": P.ERROR, "ic": P.ERROR,
                                                     "cruce": P.NO_SE_LLEGO, "escritura": P.NO_SE_LLEGO}
    assert err.errores[0].donde == "Movilidad  ·  2022" and err.errores[1].donde.endswith("2022-1")
    assert salida(muestra) == []
    texto = detalle_para_sistemas(err.errores, {"Programa": "Administración de Empresas"})
    assert "Paso: Leer la Movilidad anual" in texto and "Causa técnica: con_contrasena" in texto


def test_sin_matriz_se_detiene_en_el_paso_1(muestra, config):
    (muestra / NOMBRES["matriz"]).unlink()
    with pytest.raises(GeneracionDetenida) as e:
        gen(muestra, config)
    assert [x.titulo for x in e.value.errores] == ["Falta la Matriz de convenios"]
    assert e.value.pasos[0].estado == P.ERROR and e.value.pasos[1].estado == P.NO_SE_LLEGO


def test_programa_sin_convenios_se_detiene(muestra, config):
    with pytest.raises(GeneracionDetenida) as e:
        gen(muestra, config, "derecho")
    x = e.value.errores[0]
    assert x.titulo == "Ningún convenio aplica a Derecho" and x.etiqueta == "Sin convenios"
    assert "(6 filas)" in x.que_paso and salida(muestra) == []


@pytest.mark.parametrize("falla, causa", [(PermissionError(13, "Acceso denegado"), "sin_permiso"),
                                         (OSError(errno.ENOSPC, "No space left on device"), "disco_lleno")])
def test_no_se_pudo_guardar_borra_el_temporal(muestra, config, monkeypatch, falla, causa):
    def guardar_mal(self, ruta):
        open(ruta, "wb").write(b"a medias")
        raise falla
    monkeypatch.setattr(openpyxl.Workbook, "save", guardar_mal)
    with pytest.raises(GeneracionDetenida) as e:
        gen(muestra, config)
    x = e.value.errores[0]
    assert x.titulo == "No se pudo guardar el cuadro" and x.detalle_tecnico.startswith(causa)
    assert e.value.pasos[-1].estado == P.ERROR and e.value.pasos[3].estado == P.HECHO
    assert salida(muestra) == []                                # el temporal se borró


def test_carpeta_de_salida_imposible(muestra, config):
    (muestra / CARPETA_SALIDA).write_text("soy un archivo, no una carpeta")
    with pytest.raises(GeneracionDetenida) as e:
        gen(muestra, config)
    assert e.value.errores[0].paso == "escritura"


# ---------------------------------------------------------------- cancelar
def test_cancelar_durante_la_lectura(muestra, config):
    with pytest.raises(Cancelado):
        gen(muestra, config, cancelado=lambda: True)
    assert salida(muestra) == []


def test_cancelar_justo_antes_de_renombrar_no_deja_nada(muestra, config):
    llamadas = []

    def cancelar():
        llamadas.append(1)
        return (muestra / CARPETA_SALIDA).exists() and any((muestra / CARPETA_SALIDA).iterdir())

    with pytest.raises(Cancelado):
        gen(muestra, config, cancelado=cancelar)
    assert salida(muestra) == []


# ---------------------------------------------------------------- con los Excel reales
@pytest.mark.skipif(not (HAY_ANONIMIZADOS or ORIGINALES), reason="solo con copias anonimizadas u originales")
def test_cuadro_real_de_2022(carpeta, config, request, tmp_path):
    if "sintetica" in request.node.callspec.id:
        pytest.skip("la muestra inventada no es el cuadro real")
    import shutil
    for f in carpeta.glob("*.xls*"):
        shutil.copy(f, tmp_path / f.name)
    ws = openpyxl.load_workbook(gen(tmp_path, config).ruta)["Convenios"]
    assert ws.max_row == 17 + 88
    continental = {ws.cell(r, 5).value: ws.cell(r, 4).value for r in range(18, ws.max_row + 1)
                   if ws.cell(r, 2).value == "UNIVERSIDAD CONTINENTAL"}
    assert continental == {10: "2022\n- Experto internacional: 1", 5: "2022\n- Internacionalización en casa: 10"}
