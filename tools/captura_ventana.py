"""Capturas de la interfaz real con la muestra inventada (para revisar cómo se ve en Windows).

Uso: python tools/captura_ventana.py <carpeta_salida>
Crea la muestra en una carpeta temporal, abre la ventana principal y las ventanas de la generación, y guarda una
imagen de cada una. Lo corre GitHub Actions en Windows y sube las imágenes como artefacto «capturas-windows».
No toca la configuración real: usa una carpeta de usuario temporal.
"""
import os
import sys
import tempfile
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
from cuadro_maestro.interfaz.ventana import VentanaPrincipal  # noqa: E402
from muestra_sintetica import NOMBRES, crear_muestra  # noqa: E402

datos = TEMP / "Excel"
crear_muestra(datos)
raiz = tk.Tk()
raiz.title("Cuadro maestro internacional")
T.cargar_fuentes(raiz)
raiz.geometry("1000x920+20+20")
almacen = AlmacenConfiguracion(TEMP / "appdata", TEMP / "junto")
config = almacen.cargar().configuracion
estados = AlmacenEstado(TEMP / "appdata", TEMP / "junto")
ventana = VentanaPrincipal(raiz, almacen, config, estados, Estado(str(datos), "administracion-de-empresas", 2021, 2022))


def foto(nombre, ventana_tk=None):
    raiz.update()
    w = ventana_tk or raiz
    w.update()
    w.after(300)
    w.update()
    x, y = w.winfo_rootx(), w.winfo_rooty()
    ImageGrab.grab(bbox=(x, y, x + w.winfo_width(), y + w.winfo_height()), all_screens=True).save(SALIDA / f"{nombre}.png")


def modal_abierto():
    return next((w for w in raiz.winfo_children() if isinstance(w, tk.Toplevel) and w.winfo_viewable()), None)


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
    ventana._generado = lambda g: None
    capturar_y_cerrar("31_cuadro_generado")
    D.cuadro_generado(raiz, salida[1])
(datos / NOMBRES["ic1"]).write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\0" * 64 + "EncryptedPackage".encode("utf-16-le"))
try:
    generar(datos, config, "administracion-de-empresas", 2022, 2022)
except GeneracionDetenida as e:
    capturar_y_cerrar("43_generacion_detenida")
    D.generacion_detenida(raiz, e, {"Programa": "Administración de Empresas"})
raiz.destroy()
print("Capturas en", SALIDA, sorted(p.name for p in SALIDA.glob("*.png")))
