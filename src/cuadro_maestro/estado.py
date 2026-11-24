"""Lo que la ventana recuerda entre una apertura y otra: carpeta, programa, vigencia y la última generación.

Se guarda en los mismos dos lugares que la configuración (`estado.json`), con escritura atómica, y al abrir se usa la
copia más reciente. No tiene datos de personas: rutas, nombres de programa, horas y cantidades de avisos.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from .configuracion.almacen import escribir_atomico

NOMBRE = "estado.json"
FORMATO = "cuadro-maestro-estado"


@dataclass
class UltimaGeneracion:
    programa_id: str
    programa: str
    anio_inicio: int
    anio_fin: int
    carpeta: str
    ruta: str
    hora: str                                   # ISO, hora local
    avisos: dict = field(default_factory=dict)  # grupo -> cantidad
    cambios_sin_incluir: bool = False

    @property
    def total_avisos(self) -> int:
        return sum(self.avisos.values())


@dataclass
class Estado:
    carpeta: str | None = None
    programa_id: str | None = None
    anio_inicio: int | None = None
    anio_fin: int | None = None
    ultima: UltimaGeneracion | None = None
    guardado_en: str = ""


class AlmacenEstado:
    def __init__(self, *carpetas: Path):
        self.carpetas = [Path(c) for c in carpetas]

    def cargar(self) -> Estado:
        mejores = []
        for c in self.carpetas:
            try:
                d = json.loads((c / NOMBRE).read_text(encoding="utf-8"))
                if d.get("formato") == FORMATO:
                    mejores.append(d)
            except (OSError, ValueError):
                continue
        if not mejores:
            return Estado()
        d = max(mejores, key=lambda x: x.get("guardado_en", ""))
        ultima = d.get("ultima")
        try:
            return Estado(d.get("carpeta"), d.get("programa_id"), d.get("anio_inicio"), d.get("anio_fin"),
                          UltimaGeneracion(**ultima) if ultima else None, d.get("guardado_en", ""))
        except TypeError:
            return Estado()

    def guardar(self, estado: Estado) -> None:
        estado.guardado_en = datetime.now().isoformat()
        datos = {"formato": FORMATO, **asdict(estado)}
        contenido = json.dumps(datos, ensure_ascii=False, indent=2).encode("utf-8")
        for c in self.carpetas:
            try:
                c.mkdir(parents=True, exist_ok=True)
                escribir_atomico(c / NOMBRE, contenido)
            except OSError:
                continue
