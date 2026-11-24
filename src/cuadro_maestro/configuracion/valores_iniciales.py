"""Configuración inicial: la que se usa la primera vez y la que se restablece.

Sale de los Excel reales revisados (solo encabezados, nunca filas de datos) y de las reglas confirmadas por la
jefatura el 23-nov-2026 (docs/reglas_de_negocio.md). Todo se puede cambiar después en Configuración.
"""
import copy
import re

from ..texto import normalizar

FECHA_REGLAS_CONFIRMADAS = "2026-11-23"

# Nombre en pantalla -> encabezado de la columna "Programa - Pereira" en la matriz (tal como está escrito allí).
_PROGRAMAS = [
    ("Administración de Empresas", "Administración de empresas - Pereira"),
    ("Contaduría Pública", "Contaduría Pública - Pereira"),
    ("Administración de Negocios Internacionales", "Administración de negocios internacionales - Pereira"),
    ("Técnico Laboral en Auxiliar en Enfermería", "Técnico Laboral en Auxiliar en Enfermería - Pereira"),
    ("Enfermería", "Enfermería - Pereira"),
    ("Fisioterapia", "Fisioterapia - Pereira"),
    ("Instrumentación Quirúrgica", "Instrumentación Quirúrgica - Pereira"),
    ("Odontología", "Odontología - Pereira"),
    ("Optometría", "Optometría - Pereira"),
    ("Entrenamiento Deportivo", "Entrenamiento Deportivo - Pereira"),
    ("Tecnología en Radiología e Imágenes Diagnósticas", "Tecnología en Radiología e Imágenes Diagnósticas - Pereira"),
    ("Terapia Respiratoria", "Terapia Respiratoria - Pereira"),
    ("Especialización en Auditoría en Salud", "Especialización en Auditoria en Salud - Pereira"),
    ("Especialización en Epidemiología", "Especialización en Epidemiología - Pereira"),
    ("Especialización en Gerencia en Seguridad y Salud en el Trabajo",
     "Especialización en Gerencia en Seguridad y Salud en el Trabajo - Pereira"),
    ("Psicología", "Psicología - Pereira"),
    ("Derecho", "Derecho - Pereira"),
    ("Especialización en Contratación Pública", "Especialización en Contratación Pública - Pereira"),
    ("Especialización en Derecho Administrativo", "Especialización en Derecho Administrativo - Pereira"),
    ("Especialización en Derecho Administrativo y Constitucional",
     "Especialización en Derecho Administrativo y Constitucional - Pereira"),
    ("Arquitectura", "Arquitectura - Pereira"),
    ("Comunicación Audiovisual y Digital", "Comunicación Audiovisual y Digital - Pereira"),
    ("Tecnología en Animación y Posproducción Audiovisual", "Tecnología en Animación y Posproducción Audiovisual - Pereira"),
    ("Licenciatura en Educación Infantil", "Licenciatura en Educación Infantil - Pereira"),
    ("Ingeniería Industrial", "Ingeniería Industrial Distancia - Pereira"),
]


def identificador(texto: str) -> str:
    return re.sub(r"\s+", "-", normalizar(texto))


def _col(*sinonimos):
    """Cómo se reconoce la columna de un dato: sinónimos normalizados y, si la persona eligió una, su encabezado."""
    return {"sinonimos": [normalizar(s) for s in sinonimos], "elegida": None}


_FUENTES = [
    {
        "id": "matriz",
        "nombre": "Matriz de convenios",
        "base": True,
        "archivo": {"contiene": ["convenios"], "excluye": ["cuadro", "cm"], "patron_anio": None,
                    "patron_semestre": None},
        "hoja": {"preferida": "CONV_INTERNACIONALES"},
        "fila_encabezado": {"automatica": True, "fila": 3},
        "columnas": {
            "institucion": _col("Nombre de la institución"),
            "objeto": _col("Objeto del convenio"),
            "codigo": _col("Código alianza"),
            "tipo_convenio": _col("Tipo de convenio"),
            "fecha_inicio": _col("Fecha de inicio"),
            "fecha_fin": _col("Fecha de finalización"),
            "vigencia_anios": _col("Vigencia en años"),
            "estado": _col("Estado"),
        },
        "filtros": {},
    },
    {
        "id": "movilidad",
        "nombre": "Movilidad",
        "base": True,
        "archivo": {"contiene": ["movilidad"], "excluye": ["cuadro"], "patron_anio": r"(20\d{2})",
                    "patron_semestre": None},
        "hoja": {"preferida": "BD GENERAL"},
        "fila_encabezado": {"automatica": True, "fila": 1},
        "columnas": {
            "anio": _col("Año"),
            "semestre": _col("Semestre"),
            "vinculo": _col("Vínculo SNIES"),
            "sede": _col("Sede"),
            "programa": _col("Programa o dependencia"),
            "institucion": _col("Institución de Origen/Destino"),
            "tipo_convenio": _col("Tipo de convenio"),
        },
        "filtros": {"solo_programa_elegido": True, "solo_sede": "Pereira"},
    },
    {
        "id": "internacionalizacion_en_casa",
        "nombre": "Internacionalización en casa",
        "base": True,
        "archivo": {"contiene": ["casa"], "excluye": ["cuadro"], "patron_anio": r"(20\d{2})",
                    "patron_semestre": r"20\d{2}\s*-\s*([12])"},
        "hoja": {"preferida": None},
        "fila_encabezado": {"automatica": True, "fila": 1},
        "columnas": {
            "anio": _col("Año"),
            "semestre": _col("Semestre"),
            "programa": _col("Nombre programa, dependencia"),
            "sede": _col("Sede o seccional"),
            "institucion": _col("Entidad / organización / institución internacional vinculada"),
            "tipo_actividad": _col("Tipo de actividad"),
        },
        "filtros": {"solo_programa_elegido": True, "solo_sede": "Pereira", "omitir_sin_institucion": True,
                    "valores_sin_institucion": ["", "n a", "na", "no aplica", "ninguna"]},
    },
]

# Campo del cuadro: identificador fijo, encabezado (tal como en el cuadro del CNA), de dónde sale ("matriz",
# "reportes", "calculado", "vacio"), qué dato, tipo, si es base (no se elimina) y ancho de columna en Excel.
_CAMPOS = [
    ("numero", "No.", "calculado", "numeracion", "numero", False, 6.5),
    ("institucion", "INSTITUCIÓN CON LAS QUE SE CELEBRÓ EL CONVENIO", "matriz", "institucion", "texto", True, 39),
    ("objeto", "Breve Objeto", "matriz", "objeto", "texto", False, 64.5),
    ("resultados", "Resultados concretos: movilidad, financiación de proyectos, publicaciones, etc.", "calculado",
     "resultados", "texto_calculado", True, 47),
    ("vigencia", "Vigencia (años)", "matriz", "vigencia_anios", "numero", True, 15.5),
    ("activo", "Activo", "calculado", "activo", "opciones", True, 21.5),
    ("usuarios", "Nº de usuarios", "vacio", None, "numero", False, 12.2),
    ("no_aplica", "No Aplica", "vacio", None, "texto", False, 12.2),
]

# Tipo de persona -> valores de la columna de vínculo que lo identifican (normalizados).
_TIPOS = [
    ("Estudiante saliente", ["estudiantes en el exterior", "estudiante en el exterior"], False),
    ("Estudiante entrante", ["estudiantes extranjeros", "estudiante extranjero"], False),
    ("Experto internacional", ["experto internacional", "expertos internacionales"], False),
    ("Docente saliente", ["profesores en el exterior", "profesor en el exterior"], False),
    ("Docente entrante", ["profesores extranjeros", "profesor extranjero"], False),
    ("Administrativo saliente", ["administrativo en el exterior", "administrativos en el exterior"], False),
    ("Administrativo entrante", ["administrativo extranjero", "administrativos extranjeros"], False),
    ("Internacionalización en casa", [], True),
]

REGLAS_CONFIRMADAS = {
    "confirmadas_el": FECHA_REGLAS_CONFIRMADAS,
    "r1_convenios_que_entran": {"valor_aplica": "APLICA", "vigentes": "con_o_sin_resultados",
                                "vencidos": "solo_con_resultados"},
    "r2_asignacion": {"solo_dentro_de_vigencia": True, "preferido_movilidad": "especifico",
                      "preferido_internacionalizacion": "marco", "desempate": "inicio_mas_reciente"},
    "r3_conteo": {"movilidad": "una_por_fila", "internacionalizacion": "una_por_fila",
                  "varios_programas_cuentan_para_cada_uno": True},
    "r4_fecha_fin": {"si_no_es_fecha": "inicio_mas_vigencia"},
    "r5_activo": {"valores_activo": ["vigente"], "valores_no_activo": ["vencido", "anulado"],
                  "etiqueta_activo": "Activo", "etiqueta_no_activo": "No Activo"},
}


def configuracion_inicial() -> dict:
    """Documento completo de configuración, sin los metadatos de guardado (los pone el almacén)."""
    return copy.deepcopy({        # copia: nada de lo que se cambie después puede tocar estos valores iniciales
        "programas": [{"id": identificador(n), "nombre": n, "columna_matriz": c} for n, c in _PROGRAMAS],
        "campos": [
            {"id": i, "nombre": n, "fuente": f, "dato": d, "tipo": t, "base": b, "ancho": w}
            for i, n, f, d, t, b, w in _CAMPOS
        ],
        "fuentes": copy.deepcopy(_FUENTES),
        "equivalencias_instituciones": [],
        "equivalencias_programas": [],
        "tipos_persona": [{"id": identificador(n), "nombre": n, "valores": v, "base": b} for n, v, b in _TIPOS],
        "reglas": REGLAS_CONFIRMADAS,
    })
