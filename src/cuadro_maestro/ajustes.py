"""Lógica de Fuentes de datos (15, 22), Campos del cuadro (14) y Reglas de cruce (19), sin interfaz.

Todo lo que cambia la configuración pasa por aquí para que las pantallas solo muestren y las pruebas lo cubran.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from pathlib import Path

from .configuracion.valores_iniciales import REGLAS_CONFIRMADAS, identificador
from .cruce.avisos import NOMBRE_DATO, periodo
from .lectura.archivos import ejemplo
from .lectura.modelos import EXACTA, POR_CONFIRMAR, SIN_IDENTIFICAR, ArchivoLeido, Lectura
from .texto import normalizar

SIN_LEER = "sin_leer"
PEOR = {SIN_IDENTIFICAR: 3, POR_CONFIRMAR: 2, EXACTA: 1, SIN_LEER: 0}
PATRON_ANIO, PATRON_SEMESTRE = r"(20\d{2})", r"20\d{2}\s*-\s*([12])"
UNICO, POR_ANIO, POR_SEMESTRE = "unico", "anio", "semestre"
PREFIJO_COLUMNA_PROPIA = "col-"          # datos de la matriz que la persona agregó al crear un campo


# ---------------------------------------------------------------- fuentes: cómo se encuentra el archivo
def modo_periodo(fuente: dict) -> str:
    a = fuente["archivo"]
    if a.get("patron_semestre"):
        return POR_SEMESTRE
    return POR_ANIO if a.get("patron_anio") else UNICO


def poner_modo_periodo(fuente: dict, modo: str) -> None:
    a = fuente["archivo"]
    a["patron_anio"] = PATRON_ANIO if modo in (POR_ANIO, POR_SEMESTRE) else None
    a["patron_semestre"] = PATRON_SEMESTRE if modo == POR_SEMESTRE else None


def palabras(texto: str) -> list[str]:
    """«IntCasa, casa» -> ["intcasa", "casa"]: cada palabra separada por coma basta para reconocer el archivo."""
    return [p for p in (normalizar(x) for x in re.split(r"[,;]", texto or "")) if p]


def poner_contiene(fuente: dict, texto: str) -> list[str]:
    lista = palabras(texto)
    if not lista:
        raise ValueError("Escribe al menos una palabra que tenga el nombre del archivo.")
    fuente["archivo"]["contiene"] = lista
    return lista


def describir_archivos(fuente: dict) -> str:
    hoja = (fuente.get("hoja") or {}).get("preferida")
    return {UNICO: "Un archivo" + (f" · hoja {hoja}" if hoja else ""), POR_ANIO: "Un archivo por año",
            POR_SEMESTRE: "Dos archivos por año (1.° y 2.° semestre)"}[modo_periodo(fuente)]


def renombrar_fuente(config: dict, fuente_id: str, nombre: str) -> None:
    nombre = " ".join((nombre or "").split())
    if not nombre:
        raise ValueError("Escribe un nombre.")
    if any(normalizar(f["nombre"]) == normalizar(nombre) for f in config["fuentes"] if f["id"] != fuente_id):
        raise ValueError("Ya hay una fuente con ese nombre.")
    fuente(config, fuente_id)["nombre"] = nombre


def fuente(config: dict, fuente_id: str) -> dict:
    return next(f for f in config["fuentes"] if f["id"] == fuente_id)


# ---------------------------------------------------------------- fuentes: qué columna trae cada dato
def nombre_dato(config: dict, fuente_id: str, dato: str) -> str:
    if dato in NOMBRE_DATO:
        return NOMBRE_DATO[dato]
    campo = next((c for c in config["campos"] if c["fuente"] == fuente_id and c.get("dato") == dato), None)
    if campo:
        return f"{campo['nombre']} (campo del cuadro)"
    col = fuente(config, fuente_id)["columnas"].get(dato) or {}
    return col.get("elegida") or dato


@dataclass
class EstadoDato:
    dato: str
    nombre: str
    estado: str                         # exacta, por_confirmar, sin_identificar o sin_leer
    encabezado: str | None              # el del archivo más reciente que lo trae (o la sugerencia)
    elegida: str | None                 # la que eligió la persona (se guarda para los próximos archivos)
    por_archivo: list = field(default_factory=list)      # [(nombre de archivo, estado, encabezado)]


@dataclass
class EstadoFuente:
    id: str
    nombre: str
    archivos: str
    datos: list[EstadoDato]
    leidos: list[ArchivoLeido]
    filas_encabezado: list[tuple[str, int]]              # [(periodo o nombre, fila)]

    def cuenta(self, estado: str) -> int:
        return sum(1 for d in self.datos if d.estado == estado)

    @property
    def encabezados(self) -> list[str]:
        """Encabezados de los archivos leídos (sin repetir, el más reciente primero) para «Elegir columna…»."""
        vistos, lista = set(), []
        for a in sorted(self.leidos, key=lambda a: (a.anio or 0, a.semestre or 0), reverse=True):
            for h in a.encabezados:
                if normalizar(h) not in vistos:
                    vistos.add(normalizar(h))
                    lista.append(h)
        return lista


def estado_fuentes(config: dict, lectura: Lectura | None) -> list[EstadoFuente]:
    salida = []
    for f in config["fuentes"]:
        leidos = [a for a in (lectura.archivos if lectura else []) if a.fuente == f["id"]]
        leidos.sort(key=lambda a: (a.anio or 0, a.semestre or 0))
        datos = []
        for dato, col in f["columnas"].items():
            por_archivo = [(a.ruta.name, a.columnas[dato].estado if dato in a.columnas else SIN_IDENTIFICAR,
                            a.columnas[dato].encabezado if dato in a.columnas else None) for a in leidos]
            estado = max((e for _, e, _ in por_archivo), key=PEOR.get, default=SIN_LEER)
            encabezado = next((h for _, e, h in reversed(por_archivo) if h and e == EXACTA), None) or \
                next((h for _, _, h in reversed(por_archivo) if h), None)
            datos.append(EstadoDato(dato, nombre_dato(config, f["id"], dato), estado, encabezado, col.get("elegida"),
                                    por_archivo))
        filas = [(periodo(a.anio, a.semestre) or a.ruta.name, a.fila_encabezados) for a in leidos if a.fila_encabezados]
        salida.append(EstadoFuente(f["id"], f["nombre"], describir_archivos(f), datos, leidos, filas))
    return salida


def texto_filas_detectadas(filas: list[tuple[str, int]]) -> str:
    if not filas:
        return "Sin leer"
    if len({n for _, n in filas}) == 1:
        return f"Detectada: fila {filas[0][1]}" + (f" en {len(filas)} archivos" if len(filas) > 1 else "")
    return "Detectada: " + " · ".join(f"fila {n} en {p}" for p, n in filas)


def elegir_columna(config: dict, fuente_id: str, dato: str, encabezado: str | None) -> None:
    """Guarda la columna que la persona eligió para el dato (None la quita y vuelve a buscar por nombre)."""
    fuente(config, fuente_id)["columnas"][dato]["elegida"] = " ".join(encabezado.split()) if encabezado else None


def poner_fila_encabezados(config: dict, fuente_id: str, automatica: bool, fila: int | None = None) -> None:
    conf = fuente(config, fuente_id).setdefault("fila_encabezado", {"automatica": True, "fila": 1})
    conf["automatica"] = bool(automatica)
    if fila is not None:
        if not 1 <= int(fila) <= 50:
            raise ValueError("La fila de encabezados debe estar entre 1 y 50.")
        conf["fila"] = int(fila)


# ---------------------------------------------------------------- prueba de lectura (22)
LISTO, NO_SE_ENCONTRO, NO_SE_PUDO_LEER, SIN_ENCABEZADOS = "listo", "no_se_encontro", "no_se_pudo_leer", "sin_encabezados"


@dataclass
class FilaPrueba:
    archivo: str
    fuente: str
    nombre_fuente: str
    se_leyo_como: str | None
    fila: int | None
    exactas: int | None
    total: int | None
    estado: str                      # listo, por_confirmar, sin_identificar, no_se_encontro, no_se_pudo_leer, sin_encabezados
    cantidad: int = 0                # columnas por confirmar o sin identificar

    @property
    def con_problema(self) -> bool:
        return self.estado != LISTO

    @property
    def se_puede_arreglar(self) -> bool:
        """«Arreglar ›» abre la fuente: sirve cuando el problema es de columnas o de encabezados."""
        return self.estado in (POR_CONFIRMAR, SIN_IDENTIFICAR, SIN_ENCABEZADOS)

    @property
    def texto_estado(self) -> str:
        n = self.cantidad
        return {LISTO: "Listo", POR_CONFIRMAR: f"{n} por confirmar", SIN_IDENTIFICAR: f"{n} sin identificar",
                NO_SE_ENCONTRO: "No se encontró", NO_SE_PUDO_LEER: "No se pudo leer",
                SIN_ENCABEZADOS: "Sin encabezados"}[self.estado]


def nombre_esperado(config: dict, fuente_id: str, anio, semestre) -> str:
    """Nombre sugerido para un archivo que falta: uno que el programa sí reconoce."""
    return ejemplo(fuente(config, fuente_id), anio, semestre)


def filas_prueba(config: dict, lectura: Lectura) -> list[FilaPrueba]:
    nombres = {f["id"]: f["nombre"] for f in config["fuentes"]}
    leidos = {a.ruta: a for a in lectura.archivos}
    errores = {e.ruta: e for e in lectura.errores}
    filas = []
    for e in lectura.esperados:
        nf = nombres.get(e.fuente, e.fuente)
        if not e.encontrado:
            filas.append(FilaPrueba(nombre_esperado(config, e.fuente, e.anio, e.semestre), e.fuente, nf, None, None,
                                    None, None, NO_SE_ENCONTRO))
            continue
        if e.ruta in errores:
            filas.append(FilaPrueba(e.ruta.name, e.fuente, nf, nf, None, None, None, NO_SE_PUDO_LEER))
            continue
        a = leidos[e.ruta]
        estados = [c.estado for c in a.columnas.values()]
        exactas = estados.count(EXACTA)
        if not a.fila_encabezados:
            estado, n = SIN_ENCABEZADOS, 0
        elif SIN_IDENTIFICAR in estados:
            estado, n = SIN_IDENTIFICAR, estados.count(SIN_IDENTIFICAR)
        elif POR_CONFIRMAR in estados:
            estado, n = POR_CONFIRMAR, estados.count(POR_CONFIRMAR)
        else:
            estado, n = LISTO, 0
        filas.append(FilaPrueba(a.ruta.name, e.fuente, nf, nf, a.fila_encabezados or None, exactas, len(estados),
                                estado, n))
    return filas


def contar_prueba(filas: list[FilaPrueba]) -> dict[str, int]:
    cuenta = {LISTO: 0, POR_CONFIRMAR: 0, SIN_IDENTIFICAR: 0, NO_SE_ENCONTRO: 0, NO_SE_PUDO_LEER: 0, SIN_ENCABEZADOS: 0}
    for f in filas:
        cuenta[f.estado] += 1
    return cuenta


# ---------------------------------------------------------------- campos del cuadro (14)
DATOS_CALCULADOS = {"numeracion": "Número consecutivo", "resultados": "Movilidad + int. en casa, por año y tipo",
                    "activo": "Estado del convenio (Activo o No Activo)"}
DESCRIPCION_MATRIZ = {"vigencia_anios": "Vigencia en años (o fechas de inicio y fin)"}
FUENTES_CAMPO = {"matriz": "Matriz", "calculado": "Calculado", "vacio": "Vacío"}
TIPOS_CAMPO = {"texto": "Texto", "numero": "Número", "fecha": "Fecha", "opciones": "Opciones",
               "texto_calculado": "Texto calculado"}


def describir_campo(config: dict, campo: dict) -> str:
    if campo["fuente"] == "vacio":
        return "No se llena"
    if campo["fuente"] == "calculado":
        return DATOS_CALCULADOS.get(campo.get("dato"), campo.get("dato") or "—")
    dato = campo.get("dato")
    if dato in DESCRIPCION_MATRIZ:
        return DESCRIPCION_MATRIZ[dato]
    col = fuente(config, "matriz")["columnas"].get(dato) or {}
    return col.get("elegida") or NOMBRE_DATO.get(dato, dato or "—")


def columnas_de_la_matriz(config: dict, matriz: ArchivoLeido | None) -> list[tuple[str, str, str]]:
    """Opciones de «Columna del Excel»: [(valor, texto, estado)]. Valor = dato conocido o «enc:<encabezado>»
    (una columna de la matriz que todavía no es un dato: al guardar se agrega a la fuente)."""
    cols = fuente(config, "matriz")["columnas"]
    opciones, usados = [], set()
    for dato, col in cols.items():
        c = matriz.columnas.get(dato) if matriz else None
        enc = c.encabezado if c and c.encabezado else None
        texto = enc or col.get("elegida") or NOMBRE_DATO.get(dato, dato)
        opciones.append((dato, texto, c.estado if c else SIN_LEER))
        if enc and c.estado == EXACTA:
            usados.add(normalizar(enc))
    programas = {normalizar(c.encabezado) for c in (matriz.programas.values() if matriz else []) if c.encabezado}
    for h in (matriz.encabezados if matriz else []):
        k = normalizar(h)
        if k not in usados and k not in programas and not es_columna_de_programa(h) \
                and k not in {normalizar(t) for _, t, _ in opciones}:
            opciones.append((f"enc:{h}", h, EXACTA))
    return opciones


def es_columna_de_programa(encabezado: str) -> bool:
    """«Derecho - Bogotá», «Contaduría Pública -Bogotá»: columnas APLICA / NO APLICA de cada programa y sede. En la
    matriz real los datos del convenio van en MAYÚSCULAS y los programas no, y terminan en «- Sede» (una palabra)."""
    texto = " ".join(str(encabezado).split())
    return texto != texto.upper() and re.search(r"\s-\s*[^\s-]{3,15}$", texto) is not None


def agregar_columna_matriz(config: dict, encabezado: str) -> str:
    """Convierte una columna de la matriz en un dato que se lee (para un campo nuevo). Devuelve el identificador."""
    cols = fuente(config, "matriz")["columnas"]
    for dato, col in cols.items():
        if normalizar(encabezado) in {normalizar(s) for s in [*col.get("sinonimos", []), col.get("elegida") or ""]}:
            return dato
    base = PREFIJO_COLUMNA_PROPIA + identificador(encabezado)[:40]
    dato, n = base, 2
    while dato in cols:
        dato, n = f"{base}-{n}", n + 1
    cols[dato] = {"sinonimos": [normalizar(encabezado)], "elegida": " ".join(encabezado.split())}
    return dato


def quitar_columnas_sin_uso(config: dict) -> None:
    """Quita de la matriz las columnas agregadas por un campo que ya no existe (las de base nunca se quitan)."""
    usados = {c.get("dato") for c in config["campos"] if c["fuente"] == "matriz"}
    cols = fuente(config, "matriz")["columnas"]
    for dato in [d for d in cols if d.startswith(PREFIJO_COLUMNA_PROPIA) and d not in usados]:
        del cols[dato]


def guardar_campo(config: dict, indice: int, nombre: str, fuente_campo: str, dato: str | None, tipo: str) -> dict:
    """Crea (indice = -1) o cambia un campo. Los campos base solo cambian de nombre."""
    nombre = " ".join((nombre or "").split())
    if not nombre:
        raise ValueError("Escribe el nombre del campo.")
    campos = config["campos"]
    if any(normalizar(c["nombre"]) == normalizar(nombre) for j, c in enumerate(campos) if j != indice):
        raise ValueError("Ya hay un campo con ese nombre.")
    if indice >= 0 and campos[indice].get("base"):
        campos[indice]["nombre"] = nombre
        return campos[indice]
    if fuente_campo not in FUENTES_CAMPO:
        raise ValueError("Elige de dónde sale el dato.")
    if fuente_campo == "matriz":
        if not dato:
            raise ValueError("Elige la columna de la matriz.")
        if dato.startswith("enc:"):
            dato = agregar_columna_matriz(config, dato[4:])
    elif fuente_campo == "calculado":
        if dato not in DATOS_CALCULADOS:
            raise ValueError("Elige qué se calcula.")
        tipo = {"numeracion": "numero", "resultados": "texto_calculado", "activo": "opciones"}[dato]
    else:
        dato = None
    if indice == -1:
        ident = identificador(nombre)
        while any(c["id"] == ident for c in campos):
            ident += "-2"
        campo = {"id": ident, "nombre": nombre, "fuente": fuente_campo, "dato": dato, "tipo": tipo, "base": False,
                 "ancho": 15}
        campos.append(campo)
    else:
        campo = campos[indice]
        campo.update(nombre=nombre, fuente=fuente_campo, dato=dato, tipo=tipo)
    quitar_columnas_sin_uso(config)
    return campo


def eliminar_campo(config: dict, indice: int) -> None:
    if config["campos"][indice].get("base"):
        raise ValueError("Es un campo base: el programa lo necesita para calcular.")
    del config["campos"][indice]
    quitar_columnas_sin_uso(config)


def mover_campo(config: dict, desde: int, hasta: int) -> bool:
    campos = config["campos"]
    hasta = max(0, min(len(campos) - 1, hasta))
    if desde == hasta:
        return False
    campos.insert(hasta, campos.pop(desde))
    return True


# ---------------------------------------------------------------- reglas de cruce (19)
CLAVES_REGLAS = ["r1_convenios_que_entran", "r2_asignacion", "r3_conteo", "r4_fecha_fin", "r5_activo"]


def regla_cambiada(config: dict, clave: str) -> bool:
    return config["reglas"].get(clave) != REGLAS_CONFIRMADAS[clave]


def restablecer_reglas(config: dict, clave: str | None = None) -> None:
    for k in ([clave] if clave else CLAVES_REGLAS):
        config["reglas"][k] = copy.deepcopy(REGLAS_CONFIRMADAS[k])


def fecha_confirmada(config: dict) -> str:
    meses = "ene feb mar abr may jun jul ago sep oct nov dic".split()
    a, m, d = (config["reglas"].get("confirmadas_el") or REGLAS_CONFIRMADAS["confirmadas_el"]).split("-")
    return f"{int(d)}-{meses[int(m) - 1]}-{a}"


def carpeta_valida(carpeta) -> Path | None:
    return Path(carpeta) if carpeta and Path(carpeta).is_dir() else None


# ---------------------------------------------------------------- Ver cómo se aplican las reglas (21)
NOMBRE_REGLA = {1: "Qué convenios entran al cuadro", 2: "A qué convenio va cada registro", 3: "Qué se cuenta",
                4: "Vigencia y fecha de fin", 5: "Activo o No activo"}
ORDEN_EJEMPLOS = ["r2_preferido_movilidad", "r2_preferido_internacionalizacion_en_casa", "r2_unico_movilidad",
                  "r2_unico_internacionalizacion_en_casa", "r2_desempate", "r2_sin_vigente", "r1_entra_vencido",
                  "r1_fuera_vencido", "r1_fuera_vigente", "r1_entra_vigente", "r4_calculada", "r4_revision"]


def _miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _plural(n: int, palabra: str) -> str:
    plural = palabra + ("es" if palabra.endswith("d") else "s")
    return f"{_miles(n)} {palabra if n == 1 else plural}"


def con_reglas_confirmadas(config: dict) -> dict:
    otra = copy.deepcopy(config)
    otra["reglas"] = copy.deepcopy(REGLAS_CONFIRMADAS)
    return otra


@dataclass
class Aplicacion:
    confirmado: object                 # ResultadoCruce con las reglas confirmadas
    actual: object                     # ResultadoCruce con las reglas de hoy
    cambiadas: list[int]               # números de las reglas cambiadas

    def efecto(self) -> list[tuple[str, int, int]]:
        a, b = self.confirmado, self.actual
        return [("Convenios en el cuadro", a.convenios_en_cuadro, b.convenios_en_cuadro),
                ("Convenios sin resultados (Sin evidencia)", a.sin_resultados, b.sin_resultados),
                ("Movilidades contadas", a.movilidades_contadas, b.movilidades_contadas),
                ("Actividades de internacionalización en casa", a.actividades_contadas, b.actividades_contadas)]

    def frase_efecto(self) -> str | None:
        if not self.cambiadas:
            return None
        cambios = [(n, x, y) for n, x, y in self.efecto() if x != y]
        reglas = " y ".join(", ".join(str(n) for n in self.cambiadas).rsplit(", ", 1))
        quien = f"Tu cambio en la regla {reglas}" if len(self.cambiadas) == 1 else f"Tus cambios en las reglas {reglas}"
        if not cambios:
            return f"{quien} no cambia ninguna cifra del cuadro con estos archivos."
        a, b = self.confirmado, self.actual
        partes = []
        d = b.convenios_en_cuadro - a.convenios_en_cuadro
        d_sin = b.sin_resultados - a.sin_resultados
        if d:
            todos = ", todos sin resultados" if d == d_sin and abs(d) > 1 else ", sin resultados" if d == d_sin else ""
            partes.append(f"{'agrega' if d > 0 else 'quita'} {_plural(abs(d), 'convenio')} "
                          f"{'al' if d > 0 else 'del'} cuadro{todos}")
        if d_sin and d_sin != d:
            partes.append(f"{_plural(abs(d_sin), 'convenio')} {'más' if d_sin > 0 else 'menos'} con «Sin evidencia»")
        for n, x, y in cambios[2:]:
            unidad = "movilidad" if n.startswith("Movilidades") else "actividad"
            partes.append(f"cuenta {_plural(abs(y - x), unidad)} {'más' if y > x else 'menos'}")
        return f"{quien} " + ", ".join(partes[:-1]) + (" y " if len(partes) > 1 else "") + partes[-1] + "."

    def decisiones(self) -> list[tuple[int, str, bool]]:
        r, t = self.actual, self.actual.traza
        return [
            (1, f"{_miles(r.convenios_en_cuadro)} entran · {_miles(t.fuera_por_regla_1)} quedan fuera por no tener "
                f"resultados ({_miles(t.vigentes_fuera)} vigentes, {_miles(t.vencidos_fuera)} vencidos)", 1 in self.cambiadas),
            (2, f"{_miles(r.registros_asignados)} registros asignados · {_miles(t.sin_convenio_que_cubra)} sin convenio "
                "que cubra el año (van a Ver revisión)", 2 in self.cambiadas),
            (3, f"{_plural(r.movilidades_contadas, 'movilidad')} · {_plural(r.actividades_contadas, 'actividad')} de "
                "internacionalización en casa", 3 in self.cambiadas),
            (4, f"{_miles(t.vigencia_calculada)} vigencia{'s' if t.vigencia_calculada != 1 else ''} calculada{'s' if t.vigencia_calculada != 1 else ''} con año de inicio + vigencia · "
                f"{_miles(t.sin_fin_usable + t.sin_inicio)} sin fechas usables (van a Ver revisión)", 4 in self.cambiadas),
            (5, f"{_miles(r.activos)} activos · {_miles(r.convenios_en_cuadro - r.activos)} no activos, según la matriz "
                "de hoy", 5 in self.cambiadas),
        ]

    def ejemplos(self, cuantos=6) -> list:
        e = self.actual.traza.ejemplos
        return [e[k] for k in ORDEN_EJEMPLOS if k in e][:cuantos]


def aplicar_reglas(lectura: Lectura, config: dict, programa_id: str) -> Aplicacion:
    from .cruce import cruzar
    cambiadas = [i for i, k in enumerate(CLAVES_REGLAS, start=1) if regla_cambiada(config, k)]
    actual = cruzar(lectura, config, programa_id)
    confirmado = cruzar(lectura, con_reglas_confirmadas(config), programa_id) if cambiadas else actual
    return Aplicacion(confirmado, actual, cambiadas)
