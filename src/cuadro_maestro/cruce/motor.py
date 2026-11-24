"""Cruce: de la lectura y la configuración a las filas del cuadro de un programa y los avisos de su revisión.

Aplica las 5 reglas de Configuración › Reglas de cruce (docs/reglas_de_negocio.md):
1. Entran los convenios que APLICAN al programa; los vigentes con o sin resultados, los vencidos solo con resultados.
2. Cada registro va a un convenio de su institución que cubra su año; movilidad prefiere el específico e
   internacionalización en casa el marco; si hay varios, el de inicio más reciente. Sin convenio: a la revisión.
3. Se cuenta una movilidad o una actividad por fila; una fila con varios programas cuenta para cada uno.
4. Si la fecha de fin no es una fecha: año de inicio + vigencia en años. Sin inicio válido: a la revisión.
5. Activo o No activo según el estado de la matriz.

Solo se usan columnas exactas: una columna «por confirmar» no se usa hasta que alguien la confirme.
"""
from __future__ import annotations

from collections import defaultdict

from ..lectura import valores as V
from ..lectura.modelos import EXACTA, Lectura
from ..texto import normalizar
from . import avisos as T
from .instituciones import Equivalencias, IndiceInstituciones, parecido_al_programa, programa_coincide
from .modelos import ORDEN_GRUPOS, Convenio, FilaCuadro, ResultadoCruce

REQUERIDAS = {"matriz": ("institucion", "tipo_convenio", "fecha_inicio", "estado"),
              "movilidad": ("institucion", "programa", "vinculo"),
              "internacionalizacion_en_casa": ("institucion", "programa")}
UMBRAL_PROGRAMA_PARECIDO = 0.9


def cruzar(lectura: Lectura, config: dict, programa_id: str) -> ResultadoCruce:
    programa = next(p for p in config["programas"] if p["id"] == programa_id)
    reglas = config["reglas"]
    eq_inst = Equivalencias(config.get("equivalencias_instituciones", []))
    eq_prog = Equivalencias(config.get("equivalencias_programas", []))
    fuentes = {f["id"]: f for f in config["fuentes"]}
    hojas = {a.ruta: a.hoja for a in lectura.archivos}
    avisos = [x for a in lectura.avisos if (x := T.desde_lectura(a, lectura.carpeta, programa, hojas))]

    convenios, del_programa, indice = _convenios(lectura, programa, reglas, eq_inst, avisos)
    por_clave = defaultdict(list)
    for c in convenios:
        por_clave[c.clave].append(c)

    resultados: dict[int, dict[int, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    tipos = config["tipos_persona"]
    tipo_ic = next((t["nombre"] for t in tipos if t.get("base")), "Internacionalización en casa")
    por_vinculo = {normalizar(v): t["nombre"] for t in tipos for v in t.get("valores", [])}
    nombres_programas = {normalizar(p["nombre"]) for p in config["programas"]}
    contadas = {"movilidad": 0, "internacionalizacion_en_casa": 0}
    sin_institucion_total = 0
    r2 = reglas["r2_asignacion"]

    for archivo in lectura.archivos:
        if archivo.fuente not in ("movilidad", "internacionalizacion_en_casa"):
            continue
        origen = archivo.fuente
        if any(archivo.columnas[d].estado != EXACTA for d in REQUERIDAS[origen] if d in archivo.columnas):
            continue                       # el aviso de la columna ya está en la revisión
        usa = {d for d, c in archivo.columnas.items() if c.estado == EXACTA}
        filtros = fuentes[origen].get("filtros", {})
        vacios = frozenset(normalizar(x) for x in filtros.get("valores_sin_institucion", [])) | V.VACIOS_POR_DEFECTO
        grupos: dict[tuple, T.Grupo] = {}

        def agrupar(tipo, nombre, fila):
            g = grupos.setdefault((tipo, normalizar(nombre)), T.Grupo(archivo.ruta, origen, str(nombre).strip()))
            g.filas.append(fila)

        sin_institucion = 0
        for reg in archivo.registros:
            v = reg.valores
            sede = filtros.get("solo_sede")
            if sede and "sede" in usa and normalizar(v.get("sede")) != normalizar(sede):
                continue
            if filtros.get("solo_programa_elegido", True):
                partes = V.separar_lista(v.get("programa"))
                if not any(programa_coincide(p, programa, eq_prog) for p in partes):
                    for p in partes:
                        if (eq_prog.clave(p) not in nombres_programas
                                and parecido_al_programa(p, programa) >= UMBRAL_PROGRAMA_PARECIDO):
                            agrupar("programa_parecido", p, reg.fila)
                    continue
            anio = (V.a_anio(v.get("anio")) if "anio" in usa else None) or archivo.anio
            if anio is None or not lectura.anio_inicio <= anio <= lectura.anio_fin:
                continue
            inst = v.get("institucion")
            if V.es_vacio(inst, vacios):
                if origen == "internacionalizacion_en_casa" and filtros.get("omitir_sin_institucion", True):
                    sin_institucion += 1                 # P11: se omiten y solo se cuentan
                else:
                    agrupar("sin_convenio_declarado", "sin institución", reg.fila)
                continue
            if origen == "movilidad":
                tipo = por_vinculo.get(normalizar(v.get("vinculo")))
                if tipo is None:
                    agrupar("tipo_persona_no_reconocido", v.get("vinculo") or "(vacío)", reg.fila)
                    continue
            else:
                tipo = tipo_ic
            clave = indice.clave(inst)
            propios = por_clave.get(clave)
            if not propios:
                if indice.existe(clave):
                    agrupar("sin_convenio_del_programa", inst, reg.fila)
                elif "sin convenio" in normalizar(v.get("tipo_convenio")):
                    agrupar("sin_convenio_declarado", inst, reg.fila)
                else:
                    agrupar("institucion_sin_coincidencia", inst, reg.fila)
                continue
            candidatos = [c for c in propios if not r2["solo_dentro_de_vigencia"] or c.anio_inicio <= anio <= c.anio_fin]
            if not candidatos:
                agrupar("sin_convenio_vigente", propios[0].institucion, reg.fila)
                continue
            preferido = r2["preferido_movilidad"] if origen == "movilidad" else r2["preferido_internacionalizacion"]
            elegidos = [c for c in candidatos if c.tipo == preferido] or candidatos
            mas_antiguo = r2.get("desempate") == "inicio_mas_antiguo"
            elegido = (min if mas_antiguo else max)(elegidos, key=lambda c: (c.inicio, c.fila))
            resultados[elegido.fila][anio][tipo] += 1
            contadas[origen] += 1

        sin_institucion_total += sin_institucion
        for (tipo, _), g in grupos.items():
            avisos.append(_aviso_de_grupo(tipo, g, programa, indice))
        if sin_institucion:
            avisos.append(T.actividades_sin_institucion(archivo.ruta, sin_institucion))

    filas = _filas(convenios, resultados, reglas["r1_convenios_que_entran"])
    avisos.sort(key=lambda a: ORDEN_GRUPOS.index(a.grupo))
    return ResultadoCruce(programa, lectura.anio_inicio, lectura.anio_fin, filas, avisos,
                          archivos_leidos=len(lectura.archivos), movilidades_contadas=contadas["movilidad"],
                          actividades_contadas=contadas["internacionalizacion_en_casa"],
                          actividades_sin_institucion=sin_institucion_total, convenios_del_programa=del_programa)


def _aviso_de_grupo(tipo, g, programa, indice):
    if tipo == "institucion_sin_coincidencia":
        return T.institucion_sin_coincidencia(g, indice.sugerencias(g.nombre))
    if tipo == "sin_convenio_vigente":
        return T.sin_convenio_vigente(g)
    if tipo == "sin_convenio_del_programa":
        return T.sin_convenio_del_programa(g, programa)
    if tipo == "sin_convenio_declarado":
        return T.sin_convenio_declarado(g)
    if tipo == "tipo_persona_no_reconocido":
        return T.tipo_no_reconocido(g)
    return T.programa_parecido(g, programa)


def _convenios(lectura, programa, reglas, eq_inst, avisos):
    matriz = lectura.matriz
    if matriz is None:
        return [], 0, IndiceInstituciones([], eq_inst)
    indice = IndiceInstituciones([r.valores.get("institucion") for r in matriz.registros], eq_inst)
    col = matriz.programas.get(programa["id"])
    if col is None or col.estado != EXACTA or any(
            matriz.columnas[d].estado != EXACTA for d in REQUERIDAS["matriz"]):
        return [], 0, indice
    r1, r5 = reglas["r1_convenios_que_entran"], reglas["r5_activo"]
    aplica = normalizar(r1["valor_aplica"])
    activos = {normalizar(x) for x in r5["valores_activo"]}
    no_activos = {normalizar(x) for x in r5["valores_no_activo"]}
    convenios, del_programa = [], 0
    for r in matriz.registros:
        v = r.valores
        if normalizar(v["programas"].get(programa["id"])) != aplica or V.es_vacio(v.get("institucion")):
            continue
        del_programa += 1
        inst = str(v["institucion"]).strip()
        inicio = V.a_fecha(v.get("fecha_inicio"))
        if inicio is None:
            avisos.append(T.convenio_sin_inicio(matriz.ruta, matriz.hoja, r.fila, inst))
            continue
        fin, vigencia = V.a_fecha(v.get("fecha_fin")), V.a_entero(v.get("vigencia_anios"))
        if fin is not None:
            if fin < inicio:
                avisos.append(T.convenio_fin_antes(matriz.ruta, matriz.hoja, r.fila, inst, inicio, fin))
                continue
            anio_fin = fin.year
        elif vigencia is not None and reglas["r4_fecha_fin"]["si_no_es_fecha"] == "inicio_mas_vigencia":
            anio_fin = inicio.year + vigencia                      # P3 / regla 4
        else:
            avisos.append(T.convenio_sin_fin(matriz.ruta, matriz.hoja, r.fila, inst))
            continue
        estado = normalizar(v.get("estado"))
        activo = estado in activos
        if not activo and estado not in no_activos:
            avisos.append(T.estado_no_reconocido(matriz.ruta, matriz.hoja, r.fila, inst, v.get("estado"),
                                                 r5["etiqueta_no_activo"]))
        tipo_texto = normalizar(v.get("tipo_convenio"))
        tipo = "marco" if tipo_texto.startswith("marco") else "especifico" if tipo_texto.startswith("especific") else "otro"
        convenios.append(Convenio(r.fila, inst, indice.clave(inst), tipo, str(v.get("tipo_convenio") or "").strip(),
                                  _texto(v.get("codigo")), _texto(v.get("objeto")), inicio, inicio.year, anio_fin,
                                  vigencia, str(v.get("estado") or "").strip(), activo,
                                  {k: x for k, x in v.items() if k != "programas"}))
    return convenios, del_programa, indice


def _filas(convenios, resultados, r1):
    filas = []
    for c in convenios:
        res = {a: dict(t) for a, t in sorted(resultados.get(c.fila, {}).items())}
        con_resultados = any(res.values())
        regla = r1["vigentes"] if c.activo else r1["vencidos"]
        if regla == "solo_con_resultados" and not con_resultados:
            continue
        filas.append(FilaCuadro(0, c, res))
    filas.sort(key=lambda f: (normalizar(f.convenio.institucion), f.convenio.inicio, f.convenio.fila))
    for i, f in enumerate(filas, start=1):
        f.numero = i
    return filas


def _texto(v):
    return str(v).strip() if v is not None and str(v).strip() else None


def texto_resultados(fila: FilaCuadro, tipos_persona: list[dict]) -> str:
    """«Resultados concretos» como en el cuadro hecho a mano: cada año y debajo «- Tipo: cantidad»."""
    if not fila.total:
        return "Sin evidencia"
    orden = {t["nombre"]: i for i, t in enumerate(tipos_persona)}
    lineas = []
    for anio, por_tipo in sorted(fila.resultados.items()):
        if not por_tipo:
            continue
        lineas.append(str(anio))
        for tipo, n in sorted(por_tipo.items(), key=lambda x: orden.get(x[0], 99)):
            lineas.append(f"- {tipo}: {n}")
    return "\n".join(lineas)
