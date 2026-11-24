"""Capturas de la interfaz real con la muestra inventada (para revisar cómo se ve en Windows).

Uso: python tools/captura_ventana.py <carpeta_salida>
Crea la muestra en una carpeta temporal, abre la ventana principal y las ventanas de la generación, y guarda una
imagen de cada una. Lo corre GitHub Actions en Windows y sube las imágenes como artefacto «capturas-windows».
No toca la configuración real: usa una carpeta de usuario temporal.
"""
import os
import sys
import tempfile
import threading
import tkinter as tk
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "tests")]
SALIDA = Path(sys.argv[1] if len(sys.argv) > 1 else "capturas").resolve()
SALIDA.mkdir(parents=True, exist_ok=True)
TEMP = Path(tempfile.mkdtemp(prefix="cuadro-captura-"))
os.environ["APPDATA"] = str(TEMP / "appdata")

from PIL import ImageGrab  # noqa: E402

from cuadro_maestro.configuracion import AlmacenConfiguracion  # noqa: E402
from cuadro_maestro.estado import AlmacenEstado, Estado  # noqa: E402
from cuadro_maestro.generacion import GeneracionDetenida, generar  # noqa: E402
from cuadro_maestro.interfaz import dialogos as D  # noqa: E402
from cuadro_maestro.interfaz import tema as T  # noqa: E402
from cuadro_maestro.interfaz import flujo  # noqa: E402
from cuadro_maestro.interfaz import revision as IR  # noqa: E402
from cuadro_maestro.interfaz.app import Aplicacion  # noqa: E402
from muestra_sintetica import NOMBRES, crear_muestra  # noqa: E402

datos = TEMP / "Excel"
threading.Timer(240, lambda: (print("Tiempo agotado: alguna ventana quedó esperando"), os._exit(1))).start()
crear_muestra(datos)
raiz = tk.Tk()
raiz.title("Cuadro maestro internacional")
T.cargar_fuentes(raiz)
raiz.geometry("1000x920+20+20")
almacen = AlmacenConfiguracion(TEMP / "appdata", TEMP / "junto")
config = almacen.cargar().configuracion
estados = AlmacenEstado(TEMP / "appdata", TEMP / "junto")
estado = Estado(str(datos), "administracion-de-empresas", 2021, 2022)
app = Aplicacion(raiz, almacen, config, estados, estado)
ventana = app.ventana


def foto(nombre, ventana_tk=None):
    raiz.update()
    w = ventana_tk or raiz
    w.update()
    w.after(300)
    w.update()
    x, y = w.winfo_rootx(), w.winfo_rooty()
    ImageGrab.grab(bbox=(x, y, x + w.winfo_width(), y + w.winfo_height()), all_screens=True).save(SALIDA / f"{nombre}.png")


def modal_abierto():
    """La ventana emergente visible más reciente (puede haber una sobre otra)."""
    def todas(w):
        for h in w.winfo_children():
            if isinstance(h, tk.Toplevel):
                yield h
                yield from todas(h)
    return next((w for w in reversed(list(todas(raiz))) if w.winfo_viewable()), None)


def capturar_y_cerrar(nombre, ms=900):
    def f():
        m = modal_abierto()
        if m:
            foto(nombre, m)
            m.destroy()
    raiz.after(ms, f)


raiz.update()
foto("01_ventana_principal")
raiz.geometry("640x920")
raiz.update()
foto("02_ventana_angosta")
raiz.geometry("1000x920")

capturar_y_cerrar("03_confirmar")
D.confirmar_generacion(raiz, "Administración de Empresas", 2021, 2022, 3, 6,
                       ["Movilidad 2021", "Int. en casa 2021-1", "Int. en casa 2021-2"], "hoy 11:20", False)
params = dict(carpeta=datos, config=config, programa_id="administracion-de-empresas", anio_inicio=2021, anio_fin=2022)
raiz.after(150, lambda: foto("30_progreso", modal_abierto()))
salida = D.Progreso(raiz, params, ["Programa: Administración de Empresas", "Vigencia: 2021–2022", "7 archivos"]).mostrar()
if salida and salida[0] == "fin":
    capturar_y_cerrar("31_cuadro_generado")
    D.cuadro_generado(raiz, salida[1])
    # Ver revisión con el cuadro recién generado
    estado.ultima = flujo.ultima_generacion(salida[1], config)
    estados.guardar(estado)
    ventana.actualizar()
    foto("35_principal_con_ultimo_cuadro")
    app.abrir_revision()
    foto("10_revision_antes_de_recargar")
    # Un error de escritura en la movilidad y recargar
    import openpyxl
    from muestra_sintetica import guardar
    wb = openpyxl.load_workbook(datos / NOMBRES["movilidad"])
    wb["BD GENERAL"]["R2"] = "Univ. Ficticia del Nrte"
    guardar(wb, datos / NOMBRES["movilidad"])
    app.revision.recargar()
    foto("12_revision_despues_de_recargar")
    aviso_inst = next(a for a in app.revision.avisos() if a.tipo == "institucion_sin_coincidencia")
    capturar_y_cerrar("28_elegir_institucion", 1500)
    app.revision.elegir_institucion(aviso_inst)
    capturar_y_cerrar("13_salir_con_cambios")
    IR.salir_con_cambios(app, app.revision.recarga)
    app.volver_a_principal()
(datos / NOMBRES["ic1"]).write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\0" * 64 + "EncryptedPackage".encode("utf-16-le"))
try:
    generar(datos, config, "administracion-de-empresas", 2022, 2022)
except GeneracionDetenida as e:
    capturar_y_cerrar("43_generacion_detenida")
    D.generacion_detenida(raiz, e, {"Programa": "Administración de Empresas"})
# Vista previa, Configuración y sus modales
from cuadro_maestro.interfaz import configuracion as C  # noqa: E402
from cuadro_maestro.interfaz.vista_previa import VistaPrevia  # noqa: E402

crear_muestra(datos)                                     # la muestra intacta otra vez
estado.ultima.cambios_sin_incluir = False                # si no, cambiar la vigencia pediría generar (aviso 38)
ventana.v_carpeta.set(str(datos))
ventana.v_desde.set("2022")
ventana.actualizar()
capturar_y_cerrar("20_previsualizar", 1200)
VistaPrevia(app, str(datos), "administracion-de-empresas", 2022, 2022).mostrar()
capturar_y_cerrar("42_previsualizar_sin_convenios", 1200)
VistaPrevia(app, str(datos), "derecho", 2022, 2022).mostrar()
app.abrir_configuracion()
foto("06_configuracion")


def abrir_editando(clase, nombre, *args, accion=lambda m: m.editar(0)):
    def f():
        m = modal_abierto()
        if m:
            accion(m)
            raiz.after(500, lambda: (foto(nombre, m), m.destroy()))
    raiz.after(600, f)
    clase(app, raiz, *args).mostrar()


abrir_editando(C.ModalProgramas, "07_programas")
config["equivalencias_instituciones"].append({"como_aparece": "Univ. Ficticia del Nrte",
                                              "es": "UNIVERSIDAD FICTICIA DEL NORTE", "origen": "revision"})
abrir_editando(C.ModalEqInstituciones, "16_equivalencias_instituciones",
               ["INSTITUTO DE PRUEBA DEL SUR", "UNIVERSIDAD FICTICIA DEL NORTE"], accion=lambda m: m.crear())
abrir_editando(C.ModalTipos, "18_tipos_de_persona", ["Pasante internacional"])
abrir_editando(C.ModalCopias, "24_copias", accion=lambda m: None)
# Fuentes de datos con una columna sin identificar, Probar lectura, Campos y Reglas
from cuadro_maestro.interfaz import campos as CA  # noqa: E402
from cuadro_maestro.interfaz import fuentes as FU  # noqa: E402
from cuadro_maestro.interfaz import reglas as RE  # noqa: E402
import openpyxl  # noqa: E402
from muestra_sintetica import guardar  # noqa: E402

wb = openpyxl.load_workbook(datos / NOMBRES["movilidad"])
wb["BD GENERAL"]["C1"] = "TIPO DE PERSONA"
guardar(wb, datos / NOMBRES["movilidad"])
ventana.v_desde.set("2021")
abrir_editando(FU.ModalFuentes, "15_fuentes", accion=lambda m: m.seleccionar("movilidad"))
capturar_y_cerrar("22_probar_lectura", 1500)
FU.ProbarLectura(raiz, app).mostrar()
abrir_editando(CA.ModalCampos, "14_campos", accion=lambda m: m.editar(2))
abrir_editando(RE.ModalReglas, "19_reglas",
               accion=lambda m: m.controles[("r1_convenios_que_entran", "vencidos")].elegir("con_o_sin_resultados"))
app.volver_de_configuracion()
raiz.destroy()
print("Capturas en", SALIDA, sorted(p.name for p in SALIDA.glob("*.png")))
os._exit(0)
