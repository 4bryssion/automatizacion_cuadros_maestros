"""Configuración editable del programa y su guardado seguro en dos lugares."""
from .almacen import AlmacenConfiguracion, CopiaDeSeguridad, ErrorDeGuardado, ResultadoCarga
from .esquema import validar
from .valores_iniciales import REGLAS_CONFIRMADAS, configuracion_inicial

__all__ = ["AlmacenConfiguracion", "CopiaDeSeguridad", "ErrorDeGuardado", "ResultadoCarga", "validar",
           "configuracion_inicial", "REGLAS_CONFIRMADAS"]
