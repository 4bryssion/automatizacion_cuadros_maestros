"""Lógica de la ventana principal (sin Tkinter) y una prueba de arranque de la ventana (si hay pantalla)."""
import os
from datetime import datetime

import pytest

from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
from cuadro_maestro.estado import AlmacenEstado, Estado, UltimaGeneracion
from cuadro_maestro.interfaz import modelo as M
from cuadro_maestro.lectura.archivos import reconocer
from muestra_sintetica import NOMBRES


@pytest.fixture
def config():
    return configuracion_inicial()


def test_resumen_de_archivos_de_la_muestra(muestra, config):
    r = M.resumir(muestra, config, 2021, 2022)
    assert (r.encontrados, r.esperados, r.completo) == (3, 6, False)
    assert r.faltan == ["Movilidad 2021", "Int. en casa 2021-1", "Int. en casa 2021-2"]
    assert [f[0] for f in r.filas] == [2021, 2022] and r.filas[1][1].estado == M.ENCONTRADO
    assert r.matriz.ruta.name == NOMBRES["matriz"] and r.matriz_modificada is not None
    assert M.mensaje_faltantes(r.faltan).startswith("Faltan 3 archivos (Movilidad 2021, Int. en casa 2021-1")
    assert M.mensaje_faltantes(["Movilidad 2021"]) == "Falta Movilidad 2021. Puedes generar igual: quedará anotado en la revisión."


def test_archivo_abierto_y_carpeta_sin_archivos(muestra, tmp_path, config):
    (muestra / f"~${NOMBRES['movilidad']}").write_bytes(b"x")
    r = M.resumir(muestra, config, 2022, 2022)
    assert r.filas[0][1].aviso == "abierto en Excel"
    vacia = tmp_path / "vacia"
    vacia.mkdir()
    (vacia / "otra cosa.xlsx").write_bytes(b"")
    assert M.resumir(vacia, config, 2022, 2022).sin_archivos
    assert not M.resumir(tmp_path / "no existe", config, 2022, 2022).carpeta_existe


def test_cuando_se_puede_generar(muestra, config):
    r = M.resumir(muestra, config, 2022, 2022)
    assert M.motivo_para_no_generar(str(muestra), "x", 2022, 2022, r) is None
    assert M.motivo_para_no_generar("", "x", 2022, 2022, r) == "Elige la carpeta con los Excel."
    assert M.motivo_para_no_generar(str(muestra), None, 2022, 2022, r) == "Elige el programa."
    assert "mayor" in M.motivo_para_no_generar(str(muestra), "x", 2023, 2022, r)
    (muestra / NOMBRES["matriz"]).unlink()
    assert "Matriz" in M.motivo_para_no_generar(str(muestra), "x", 2022, 2022, M.resumir(muestra, config, 2022, 2022))


def test_fechas_en_palabras():
    ahora = datetime(2026, 11, 24, 15, 0)
    assert M.cuando(datetime(2026, 11, 24, 14, 32), ahora) == "hoy 14:32"
    assert M.cuando(datetime(2026, 11, 23, 9, 5), ahora) == "ayer 09:05"
    assert M.cuando(datetime(2026, 11, 2, 9, 5), ahora) == "02/11/2026 09:05"
    assert M.vigencia(2022, 2022) == "2022" and M.vigencia(2019, 2023) == "2019–2023"


def test_los_nombres_de_la_ayuda_se_reconocen(config):
    """La ayuda de «Carpeta con los Excel» propone estos nombres: el programa debe reconocerlos."""
    f = {x["id"]: x for x in config["fuentes"]}
    assert reconocer("Convenios.xlsx", f["matriz"])
    assert reconocer("Movilidad_2021.xlsx", f["movilidad"])
    assert reconocer("IntCasa_2021-1.xlsx", f["internacionalizacion_en_casa"])
    assert not reconocer("Cuadro maestro - Convenios.xlsx", f["matriz"])


def test_el_estado_se_guarda_en_los_dos_lugares_y_gana_el_mas_reciente(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    almacen = AlmacenEstado(a, b)
    e = Estado("C:/x", "fisioterapia", 2019, 2023,
               UltimaGeneracion("fisioterapia", "Fisioterapia", 2019, 2023, "C:/x", "C:/x/c.xlsx",
                                "2026-11-24T14:32:00", {"excel": 2, "programa": 4, "informativo": 2}))
    almacen.guardar(e)
    assert (a / "estado.json").exists() and (b / "estado.json").exists()
    (a / "estado.json").write_text("dañado", encoding="utf-8")
    leido = almacen.cargar()
    assert leido.programa_id == "fisioterapia" and leido.ultima.total_avisos == 8


def _hay_pantalla():
    try:
        import tkinter
        r = tkinter.Tk()
        r.destroy()
        return True
    except Exception:   # noqa: BLE001
        return False


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_la_ventana_principal_arranca_y_reacciona(muestra, tmp_path, config):
    import tkinter as tk

    from cuadro_maestro.configuracion import AlmacenConfiguracion
    from cuadro_maestro.interfaz import tema as T
    from cuadro_maestro.interfaz.ventana import VentanaPrincipal
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        almacen = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
        cfg = almacen.cargar().configuracion
        estados = AlmacenEstado(tmp_path / "u", tmp_path / "p")
        v = VentanaPrincipal(raiz, almacen, cfg, estados,
                             Estado(str(muestra), "administracion-de-empresas", 2022, 2022))
        raiz.update()
        assert v.chip.cget("text") == "3 de 3 encontrados" and v.b_generar.activo
        v.v_desde.set("2023")
        raiz.update()
        assert not v.b_generar.activo and "mayor" in v.lbl_vig_error.cget("text")
        assert estados.cargar().anio_inicio == 2023
    finally:
        raiz.destroy()


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_ver_revision_recarga_y_marca_cambios_sin_incluir(muestra, tmp_path, config):
    import tkinter as tk

    import openpyxl

    from cuadro_maestro.configuracion import AlmacenConfiguracion
    from cuadro_maestro.generacion import generar
    from cuadro_maestro.interfaz import flujo
    from cuadro_maestro.interfaz import tema as T
    from cuadro_maestro.interfaz.app import Aplicacion
    from muestra_sintetica import guardar
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        almacen = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
        cfg = almacen.cargar().configuracion
        estados = AlmacenEstado(tmp_path / "u", tmp_path / "p")
        estado = Estado(str(muestra), "administracion-de-empresas", 2022, 2022)
        app = Aplicacion(raiz, almacen, cfg, estados, estado)
        g = generar(muestra, cfg, "administracion-de-empresas", 2022, 2022, logo=None)
        estado.ultima = flujo.ultima_generacion(g, cfg)
        app.abrir_revision()
        raiz.update()
        assert len(app.revision.avisos()) == 4 and not estado.ultima.cambios_sin_incluir
        wb = openpyxl.load_workbook(muestra / NOMBRES["movilidad"])
        wb["BD GENERAL"]["R2"] = "Univ. Ficticia del Nrte"
        guardar(wb, muestra / NOMBRES["movilidad"])
        app.revision.recargar()
        raiz.update()
        assert estado.ultima.cambios_sin_incluir and estado.ultima.filas_cambian == 1
        assert estados.cargar().ultima.cambios_sin_incluir           # queda guardado por si el programa se cierra
        assert len(app.revision.recarga.comparacion.nuevos) == 1
    finally:
        raiz.destroy()


def _descendientes(w):
    for h in w.winfo_children():
        yield h
        yield from _descendientes(h)


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_modales_de_configuracion_crean_editan_y_eliminan(muestra, tmp_path):
    import tkinter as tk

    from cuadro_maestro.configuracion import AlmacenConfiguracion
    from cuadro_maestro.interfaz import configuracion as C
    from cuadro_maestro.interfaz import tema as T
    from cuadro_maestro.interfaz.app import Aplicacion
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        almacen = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
        app = Aplicacion(raiz, almacen, almacen.cargar().configuracion, AlmacenEstado(tmp_path / "u", tmp_path / "p"),
                         Estado(str(muestra), "administracion-de-empresas", 2022, 2022))
        # Programas: renombrar conserva el identificador; crear propone la columna «- Pereira»
        m = C.ModalProgramas(app)
        i = next(n for n, p in enumerate(app.config["programas"]) if p["id"] == "derecho")
        m.editar(i)
        raiz.update()
        campos = [w for w in _descendientes(m.lista) if isinstance(w, tk.Entry)]     # solo el editor tiene campos
        campos[0].delete(0, "end")
        campos[0].insert(0, "Derecho (Pereira)")
        m.guardar_edicion()
        raiz.update()
        prog = next(p for p in app.config["programas"] if p["id"] == "derecho")
        assert prog["nombre"] == "Derecho (Pereira)" and almacen.actual["programas"] == app.config["programas"]
        assert "Derecho (Pereira)" in app.ventana.cb_programa.cget("values")
        m.crear()
        raiz.update()
        entradas = [w for w in _descendientes(m.lista) if isinstance(w, tk.Entry)]
        entradas[0].insert(0, "Medicina")
        m.guardar_edicion()
        raiz.update()
        assert {"id": "medicina", "nombre": "Medicina", "columna_matriz": "Medicina - Pereira"} in app.config["programas"]
        m.pedir_eliminar(next(n for n, p in enumerate(app.config["programas"]) if p["id"] == "medicina"))
        m.eliminar_elemento(next(n for n, p in enumerate(app.config["programas"]) if p["id"] == "medicina"))
        m.guardado()
        assert len(app.config["programas"]) == 25
        m.destroy()
        # Tipos: el tipo base no se elimina (candado) y un valor repetido en otro tipo se rechaza
        t = C.ModalTipos(app)
        base = len(app.config["tipos_persona"]) - 1
        t.editar(0)
        raiz.update()
        assert app.config["tipos_persona"][base]["base"]
        t.destroy()
        # Copias: crear una copia ahora
        c = C.ModalCopias(app)
        c.crear()
        assert any(x.motivo == "creada_por_ti" for x in almacen.copias_de_seguridad())
        c.destroy()
        # La pantalla de Configuración muestra los conteos
        app.abrir_configuracion()
        raiz.update()
        textos = [w.cget("text") for w in _descendientes(app.pantalla_config) if isinstance(w, tk.Label)]
        assert "25 programas" in textos and "8 tipos" in textos
    finally:
        raiz.destroy()
