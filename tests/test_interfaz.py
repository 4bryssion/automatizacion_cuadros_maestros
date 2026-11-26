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


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_fuentes_campos_y_reglas(muestra, tmp_path):
    import tkinter as tk

    import openpyxl

    from cuadro_maestro.configuracion import AlmacenConfiguracion
    from cuadro_maestro.interfaz import tema as T
    from cuadro_maestro.interfaz.app import Aplicacion
    from cuadro_maestro.interfaz.campos import ModalCampos
    from cuadro_maestro.interfaz.fuentes import ModalFuentes, ProbarLectura
    from cuadro_maestro.interfaz.reglas import ModalReglas
    from muestra_sintetica import guardar
    wb = openpyxl.load_workbook(muestra / NOMBRES["movilidad"])
    wb["BD GENERAL"]["C1"] = "TIPO DE PERSONA"
    guardar(wb, muestra / NOMBRES["movilidad"])
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        almacen = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
        app = Aplicacion(raiz, almacen, almacen.cargar().configuracion, AlmacenEstado(tmp_path / "u", tmp_path / "p"),
                         Estado(str(muestra), "administracion-de-empresas", 2022, 2022))
        raiz.update()
        lectura = __import__("cuadro_maestro.lectura", fromlist=["leer_carpeta"]).leer_carpeta(
            muestra, app.config, 2022, 2022)
        # Fuentes: la columna sin identificar se elige y se guarda
        m = ModalFuentes(app, fuente_id="movilidad", lectura=lectura)
        raiz.update()
        textos = [w.cget("text") for w in _descendientes(m) if isinstance(w, tk.Label)]
        assert "1 sin identificar" in textos and "Sin identificar" in textos
        e = m.estados["movilidad"]
        dato = next(d for d in e.datos if d.dato == "vinculo")
        assert "TIPO DE PERSONA" in e.encabezados
        m.lectura = None                       # sin releer (en las pruebas no hay ventana de espera)
        m.carpeta = None
        from cuadro_maestro import ajustes as A
        A.elegir_columna(app.config, "movilidad", dato.dato, "TIPO DE PERSONA")
        m.cambio()
        assert almacen.actual["fuentes"][1]["columnas"]["vinculo"]["elegida"] == "TIPO DE PERSONA"
        m.seleccionar("internacionalizacion_en_casa")
        m.opc_modo.elegir(A.POR_ANIO)
        assert app.config["fuentes"][2]["archivo"]["patron_semestre"] is None
        m.opc_modo.elegir(A.POR_SEMESTRE)
        m.renombrando = True
        m.pintar()
        m.guardar_nombre()
        m.destroy()
        p = ProbarLectura(raiz, app, lectura)
        raiz.update()
        textos = [w.cget("text") for w in _descendientes(p) if isinstance(w, tk.Label)]
        assert "1 sin identificar" in textos and "Arreglar ›" in textos
        p.destroy()
        # Campos: crear uno con otra columna de la matriz, ordenar y eliminar
        c = ModalCampos(app, matriz=lectura.matriz)
        raiz.update()
        c.crear()
        raiz.update()
        c.v_nombre_edicion.set("País")
        c.opc_columna.elegir("enc:PAÍS")
        c.guardar_edicion()
        assert app.config["campos"][-1]["dato"] == "col-pais" and almacen.actual["campos"][-1]["nombre"] == "País"
        c.mover(len(app.config["campos"]) - 1, 1)
        assert app.config["campos"][1]["nombre"] == "País"
        c.pedir_eliminar(1)
        raiz.update()
        c.confirmar_eliminacion()
        assert all(x["nombre"] != "País" for x in app.config["campos"])
        c.destroy()
        # Reglas: cambiar marca «Cambiada» y se restablece
        r = ModalReglas(app)
        raiz.update()
        r.controles[("r1_convenios_que_entran", "vencidos")].elegir("con_o_sin_resultados")
        textos = [w.cget("text") for w in _descendientes(r) if isinstance(w, tk.Label)]
        assert "Cambiada" in textos and "5 reglas · 1 cambiada" in textos
        r.controles[("r3_conteo", "varios_programas_cuentan_para_cada_uno")].alternar()
        assert almacen.actual["reglas"]["r3_conteo"]["varios_programas_cuentan_para_cada_uno"] is False
        r.restablecer()
        assert not A.regla_cambiada(app.config, "r1_convenios_que_entran")
        r.destroy()
    finally:
        raiz.destroy()


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_ver_como_se_aplican_y_exportar_importar(muestra, tmp_path):
    import tkinter as tk

    from cuadro_maestro.configuracion import AlmacenConfiguracion
    from cuadro_maestro.interfaz import tema as T
    from cuadro_maestro.interfaz.app import Aplicacion
    from cuadro_maestro.interfaz.intercambio import ModalIntercambio
    from cuadro_maestro.interfaz.reglas import VerComoSeAplican
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        almacen = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
        app = Aplicacion(raiz, almacen, almacen.cargar().configuracion, AlmacenEstado(tmp_path / "u", tmp_path / "p"),
                         Estado(str(muestra), "administracion-de-empresas", 2022, 2022))
        raiz.update()
        cfg = app.config
        cfg["reglas"]["r1_convenios_que_entran"]["vencidos"] = "con_o_sin_resultados"
        app.guardar_config()
        from cuadro_maestro import ajustes as A
        from cuadro_maestro.lectura import leer_carpeta
        aplicacion = A.aplicar_reglas(leer_carpeta(muestra, app.config, 2022, 2022), app.config,
                                      "administracion-de-empresas")
        from cuadro_maestro.interfaz import dialogos
        original = dialogos.en_espera
        dialogos.en_espera = lambda duena, trabajo, *a, **k: aplicacion      # sin la ventana de espera
        try:
            v = VerComoSeAplican(app)
        finally:
            dialogos.en_espera = original
        raiz.update()
        textos = [w.cget("text") for w in _descendientes(v) if isinstance(w, tk.Label)]
        assert "1 regla cambiada" in textos and any(t.startswith("Tu cambio en la regla 1") for t in textos)
        v.destroy()
        # Exportar y volver a importar (combinar) con una copia «Antes de importar»
        m = ModalIntercambio(app)
        m.carpeta = tmp_path
        m.v_nombre.set("mi configuracion")
        ruta = m.exportar()
        assert ruta.name == "mi configuracion.json" and ruta.exists()
        app.config["equivalencias_programas"].append({"como_aparece": "Admin", "es": "Administración de Empresas",
                                                      "origen": "tu"})
        app.guardar_config()
        m.elegir_archivo(str(ruta))
        textos = [w.cget("text") for w in _descendientes(m) if isinstance(w, tk.Label)]
        assert "−1" not in textos                  # combinar no quita la equivalencia nueva
        m.modo.set("reemplazar")
        m.pintar()
        textos = [w.cget("text") for w in _descendientes(m) if isinstance(w, tk.Label)]
        assert "−1" in textos                      # reemplazar sí (el archivo no la tiene)
        m.importar()
        assert app.config["equivalencias_programas"] == [] and almacen.actual["equivalencias_programas"] == []
        assert any(c.motivo == "antes_de_importar" for c in almacen.copias_de_seguridad())
        m.elegir_archivo(str(tmp_path / "no existe.json"))
        assert "No se pudo abrir" in m.error_archivo
        m.destroy()
    finally:
        raiz.destroy()


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_asistente_gemini_y_confirmar_sugerencias(muestra, tmp_path):
    import tkinter as tk

    import openpyxl

    from cuadro_maestro.configuracion import AlmacenConfiguracion
    from cuadro_maestro.cruce import cruzar
    from cuadro_maestro.interfaz import dialogos
    from cuadro_maestro.interfaz import tema as T
    from cuadro_maestro.interfaz.app import Aplicacion
    from cuadro_maestro.interfaz.gemini import ModalGemini, ModalSugerencias
    from cuadro_maestro.lectura import leer_carpeta
    from cuadro_maestro import sugerencias as S
    from muestra_sintetica import guardar
    wb = openpyxl.load_workbook(muestra / NOMBRES["movilidad"])
    wb["BD GENERAL"]["R2"] = "Univ. Ficticia del Nrte"
    guardar(wb, muestra / NOMBRES["movilidad"])
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        almacen = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
        app = Aplicacion(raiz, almacen, almacen.cargar().configuracion, AlmacenEstado(tmp_path / "u", tmp_path / "p"),
                         Estado(str(muestra), "administracion-de-empresas", 2022, 2022))
        raiz.update()
        contexto = (str(muestra), "administracion-de-empresas", 2022, 2022)
        original = dialogos.en_espera
        dialogos.en_espera = lambda duena, trabajo, *a, **k: trabajo()       # sin la ventana de espera
        try:
            g = ModalGemini(app, contexto=contexto)
        finally:
            dialogos.en_espera = original
        raiz.update()
        assert [p.como_aparece for p in g.preguntas] == ["Univ. Ficticia del Nrte"]
        g.quitadas.add("I1")                     # quitar lo que no sea una institución
        assert "Univ. Ficticia" not in g.mensaje
        g.quitadas.clear()
        g.copiar_y_abrir(abrir_navegador=False)
        assert raiz.clipboard_get().startswith("Ayúdame a emparejar") and g.paso == "respuesta"
        g.revisar("I1 → UNIVERSIDAD FICTICIA DEL NORTE")
        textos = [w.cget("text") for w in _descendientes(g) if isinstance(w, tk.Label)]
        assert "Por confirmar" in textos and "1 de 1 seleccionadas" in textos
        g.guardar()
        assert app.config["equivalencias_instituciones"][0]["origen"] == "gemini"
        assert almacen.actual["equivalencias_instituciones"] == app.config["equivalencias_instituciones"]
        # Confirmar sugerencias: con la equivalencia quitada vuelve a aparecer
        app.config["equivalencias_instituciones"] = []
        app.guardar_config()
        lectura = leer_carpeta(muestra, app.config, 2022, 2022)
        r = cruzar(lectura, app.config, "administracion-de-empresas")
        m = ModalSugerencias(app, raiz, r.avisos, "Administración de Empresas", 2022, 2022, str(muestra))
        raiz.update()
        assert len(m.lista) == 1 and not m.lista[0].marcada
        m.lista[0].marcada = True
        m.pintar()
        m.confirmar()
        assert app.config["equivalencias_instituciones"][0]["es"] == "UNIVERSIDAD FICTICIA DEL NORTE"
        assert S.sugerencias_del_programa(cruzar(leer_carpeta(muestra, app.config, 2022, 2022), app.config,
                                                 "administracion-de-empresas").avisos, app.config) == []
    finally:
        raiz.destroy()


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_un_modal_que_se_cierra_mientras_se_dibuja_no_falla(monkeypatch):
    """En Windows el modal se dibuja invisible antes de aparecer; si en ese momento ya terminó (una generación
    corta), no debe fallar al tomar el foco."""
    import tkinter as tk
    from cuadro_maestro.interfaz import dialogos as D
    from cuadro_maestro.interfaz import tema as T
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        monkeypatch.setattr(D.sys, "platform", "win32")
        m = D.Modal(raiz, "Prueba")
        m.after(0, lambda: m.cerrar("listo"))
        assert m.mostrar() == "listo"
    finally:
        raiz.destroy()


@pytest.mark.skipif(not _hay_pantalla(), reason="sin Tkinter o sin pantalla")
def test_la_vista_previa_lista_todos_los_avisos(muestra, tmp_path):
    """Antes solo se veían los 3 primeros y la tarjeta decía «Ver abajo»: ahora están todos (desplazando)."""
    import tkinter as tk

    from cuadro_maestro.configuracion import AlmacenConfiguracion
    from cuadro_maestro.interfaz import tema as T
    from cuadro_maestro.interfaz.app import Aplicacion
    from cuadro_maestro.interfaz.vista_previa import VistaPrevia
    raiz = tk.Tk()
    try:
        T.cargar_fuentes(raiz)
        almacen = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
        app = Aplicacion(raiz, almacen, almacen.cargar().configuracion, AlmacenEstado(tmp_path / "u", tmp_path / "p"),
                         Estado(str(muestra), "administracion-de-empresas", 2021, 2023))
        vp = VistaPrevia(app, str(muestra), "administracion-de-empresas", 2021, 2023)
        raiz.update()

        def textos(w):
            yield str(w.cget("text")) if "text" in w.keys() else ""
            for h in w.winfo_children():
                yield from textos(h)
        todo = list(textos(vp))
        assert len(vp.r.avisos) > 3
        for a in vp.r.avisos:
            assert any(t.startswith(a.titulo) for t in todo), a.titulo
        assert not any("en la carpeta elegida" not in t and str(muestra) in t and t.startswith("Falta") for t in todo)
        vp.destroy()
    finally:
        raiz.destroy()
