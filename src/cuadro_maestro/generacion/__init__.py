"""Generación del cuadro maestro: proceso de 5 pasos, escritura del Excel y hoja de errores."""
from .errores import ErrorGeneracion, detalle_para_sistemas
from .escritor import construir_libro, escribir
from .nombre import CARPETA_SALIDA, nombre_cuadro
from .proceso import Cancelado, Generacion, GeneracionDetenida, generar

__all__ = ["generar", "Generacion", "GeneracionDetenida", "Cancelado", "ErrorGeneracion", "detalle_para_sistemas",
           "escribir", "construir_libro", "nombre_cuadro", "CARPETA_SALIDA"]
