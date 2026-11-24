"""Fuentes de datos, Probar lectura, Campos del cuadro y Reglas de cruce (lógica, sin pantalla)."""
import openpyxl
import pytest

from cuadro_maestro import ajustes as A
from cuadro_maestro.configuracion.valores_iniciales import REGLAS_CONFIRMADAS, configuracion_inicial
from cuadro_maestro.cruce import cruzar
from cuadro_maestro.generacion import generar
from cuadro_maestro.lectura import leer_carpeta
from cuadro_maestro.lectura.modelos import EXACTA, POR_CONFIRMAR, SIN_IDENTIFICAR
from muestra_sintetica import NOMBRES, guardar

ADMIN = "administracion-de-empresas"


@pytest.fixture
def config():
    return configuracion_inicial()


def editar(ruta, hoja, cambios):
    wb = openpyxl.load_workbook(ruta)
    ws = wb[hoja] if hoja else wb.worksheets[0]
    for celda, valor in cambios.items():
        ws[celda] = valor
    guardar(wb, ruta)


def estado(config, lectura, fuente_id, dato):
    e = next(x for x in A.estado_fuentes(config, lectura) if x.id == fuente_id)
    return next(d for d in e.datos if d.dato == dato)


# ---------------------------------------------------------------- Fuentes de datos
def test_estado_de_las_fuentes_con_la_muestra(muestra, config):
    lectura = leer_carpeta(muestra, config, 2022, 2022)
    estados = {e.id: e for e in A.estado_fuentes(config, lectura)}
    assert estados["matriz"].archivos == "Un archivo · hoja CONV_INTERNACIONALES"
    assert estados["movilidad"].archivos == "Un archivo por año"
    assert estados["internacionalizacion_en_casa"].archivos == "Dos archivos por año (1.° y 2.° semestre)"
    assert all(d.estado == EXACTA for e in estados.values() for d in e.datos)
    ic = estados["internacionalizacion_en_casa"]
    assert len(ic.leidos) == 2 and "AÑO" in ic.encabezados
    assert A.texto_filas_detectadas(ic.filas_encabezado).startswith("Detectada: ")
    sin = A.estado_fuentes(config, None)
    assert all(d.estado == A.SIN_LEER for e in sin for d in e.datos)


def test_columna_sin_identificar_se_elige_y_queda_para_los_proximos(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"C1": "TIPO DE PERSONA"})       # antes «VINCULO SNIES (*)»
    d = estado(config, leer_carpeta(muestra, config, 2022, 2022), "movilidad", "vinculo")
    assert d.estado == SIN_IDENTIFICAR and d.nombre == "Vínculo"
    A.elegir_columna(config, "movilidad", "vinculo", "  TIPO DE  PERSONA ")
    d = estado(config, leer_carpeta(muestra, config, 2022, 2022), "movilidad", "vinculo")
    assert (d.estado, d.encabezado, d.elegida) == (EXACTA, "TIPO DE PERSONA", "TIPO DE PERSONA")
    A.elegir_columna(config, "movilidad", "vinculo", None)                                 # quitar la elegida
    assert estado(config, leer_carpeta(muestra, config, 2022, 2022), "movilidad", "vinculo").estado == SIN_IDENTIFICAR


def test_columna_por_confirmar_y_su_sugerencia(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"C1": "VINCULO SNIES DEL PARTICIPANTE"})
    d = estado(config, leer_carpeta(muestra, config, 2022, 2022), "movilidad", "vinculo")
    assert d.estado == POR_CONFIRMAR and d.encabezado == "VINCULO SNIES DEL PARTICIPANTE"
    A.elegir_columna(config, "movilidad", "vinculo", d.encabezado)                         # «Confirmar»
    assert estado(config, leer_carpeta(muestra, config, 2022, 2022), "movilidad", "vinculo").estado == EXACTA


def test_como_se_encuentra_el_archivo(muestra, config):
    f = A.fuente(config, "internacionalizacion_en_casa")
    assert A.modo_periodo(f) == A.POR_SEMESTRE and A.modo_periodo(A.fuente(config, "matriz")) == A.UNICO
    with pytest.raises(ValueError):
        A.poner_contiene(f, " , ")
    assert A.poner_contiene(f, "Extensión, Internacionalización en casa") == ["extension", "internacionalizacion en casa"]
    assert A.nombre_esperado(config, f["id"], 2021, 1) == "Extension_2021-1.xlsx"     # el ejemplo se sigue reconociendo
    A.poner_modo_periodo(f, A.POR_ANIO)
    assert f["archivo"]["patron_semestre"] is None and f["archivo"]["patron_anio"]
    lectura = leer_carpeta(muestra, config, 2022, 2022)
    assert [e.semestre for e in lectura.esperados if e.fuente == f["id"]] == [None]       # ahora uno por año
    A.poner_modo_periodo(f, A.POR_SEMESTRE)
    assert A.modo_periodo(f) == A.POR_SEMESTRE


def test_fila_de_encabezados_fija(muestra, config):
    A.poner_fila_encabezados(config, "movilidad", False, 2)                               # la fila 2 son datos
    d = estado(config, leer_carpeta(muestra, config, 2022, 2022), "movilidad", "institucion")
    assert d.estado != EXACTA
    with pytest.raises(ValueError):
        A.poner_fila_encabezados(config, "movilidad", False, 0)
    A.poner_fila_encabezados(config, "movilidad", True)
    assert estado(config, leer_carpeta(muestra, config, 2022, 2022), "movilidad", "institucion").estado == EXACTA


def test_cambiar_nombre_de_una_fuente_se_ve_en_los_avisos(muestra, config):
    with pytest.raises(ValueError):
        A.renombrar_fuente(config, "movilidad", "Matriz de convenios")
    A.renombrar_fuente(config, "movilidad", "Movilidad saliente y entrante")
    r = cruzar(leer_carpeta(muestra, config, 2021, 2022), config, ADMIN)
    falta = next(a for a in r.avisos if a.tipo == "falta_archivo")
    assert "Movilidad saliente y entrante 2021" in falta.titulo
    A.renombrar_fuente(config, "movilidad", "Movilidad")                                   # los nombres son globales


# ---------------------------------------------------------------- Probar lectura
def test_probar_lectura(muestra, config):
    editar(muestra / NOMBRES["movilidad"], "BD GENERAL", {"C1": "TIPO DE PERSONA"})
    filas = A.filas_prueba(config, leer_carpeta(muestra, config, 2021, 2022))
    por_archivo = {f.archivo: f for f in filas}
    assert por_archivo[NOMBRES["matriz"]].estado == A.LISTO and por_archivo[NOMBRES["matriz"]].fila == 3
    mov = por_archivo[NOMBRES["movilidad"]]
    assert (mov.estado, mov.cantidad, mov.texto_estado, mov.se_puede_arreglar) == \
        (SIN_IDENTIFICAR, 1, "1 sin identificar", True)
    assert mov.exactas == mov.total - 1
    faltan = [f for f in filas if f.estado == A.NO_SE_ENCONTRO]
    assert [f.archivo for f in faltan] == ["Movilidad_2021.xlsx", "IntCasa_2021-1.xlsx", "IntCasa_2021-2.xlsx"]
    assert not faltan[0].se_puede_arreglar
    cuenta = A.contar_prueba(filas)
    assert cuenta[A.LISTO] == 3 and cuenta[A.NO_SE_ENCONTRO] == 3 and cuenta[SIN_IDENTIFICAR] == 1


def test_probar_lectura_con_archivo_que_no_se_puede_leer(muestra, config):
    (muestra / NOMBRES["movilidad"]).write_bytes(b"esto no es un xlsx")
    filas = A.filas_prueba(config, leer_carpeta(muestra, config, 2022, 2022))
    mov = next(f for f in filas if f.fuente == "movilidad")
    assert mov.estado == A.NO_SE_PUDO_LEER and not mov.se_puede_arreglar


# ---------------------------------------------------------------- Campos del cuadro
def test_campo_nuevo_con_otra_columna_de_la_matriz(muestra, config):
    matriz = leer_carpeta(muestra, config, 1, 0).matriz
    opciones = A.columnas_de_la_matriz(config, matriz)
    valores = [v for v, _, _ in opciones]
    assert "codigo" in valores and "enc:PAÍS" in valores
    assert not any("Pereira" in t for _, t, _ in opciones)                                # las de programas no
    A.guardar_campo(config, -1, "País", "matriz", "enc:PAÍS", "texto")
    campo = config["campos"][-1]
    assert campo["dato"] == "col-pais" and A.fuente(config, "matriz")["columnas"]["col-pais"]["elegida"] == "PAÍS"
    assert A.describir_campo(config, campo) == "PAÍS"
    g = generar(muestra, config, ADMIN, 2022, 2022, logo=None)
    ws = openpyxl.load_workbook(g.ruta).worksheets[0]
    cab = next(r for r in ws.iter_rows(values_only=True) if "País" in r)
    assert cab[-1] == "País"
    datos = [r[-1] for r in ws.iter_rows(min_row=16, values_only=True) if r[1]]
    assert datos and all(isinstance(x, str) and x for x in datos)
    # eliminar el campo quita la columna agregada de la matriz
    A.eliminar_campo(config, len(config["campos"]) - 1)
    assert "col-pais" not in A.fuente(config, "matriz")["columnas"]


def test_columnas_de_programas_no_se_ofrecen_como_campo():
    assert A.es_columna_de_programa("Derecho - Bogotá") and A.es_columna_de_programa("Contaduría Pública -Bogotá")
    assert A.es_columna_de_programa("Administración de Empresas - Pereira")
    assert not A.es_columna_de_programa("PAÍS") and not A.es_columna_de_programa("CARGO O DEPENDENDENCIA")
    assert not A.es_columna_de_programa("OTROS (CUALQUIER OTRO TIPO DE ACTIVIDAD DE MUTUO BENEFICIO)")


def test_campos_base_y_validaciones(config):
    inst = next(i for i, c in enumerate(config["campos"]) if c["id"] == "institucion")
    A.guardar_campo(config, inst, "Institución", "vacio", None, "numero")                  # solo cambia el nombre
    c = config["campos"][inst]
    assert (c["nombre"], c["fuente"], c["dato"], c["tipo"]) == ("Institución", "matriz", "institucion", "texto")
    with pytest.raises(ValueError):
        A.eliminar_campo(config, inst)
    with pytest.raises(ValueError):
        A.guardar_campo(config, -1, "institución", "vacio", None, "texto")                 # nombre repetido
    with pytest.raises(ValueError):
        A.guardar_campo(config, -1, "Código", "matriz", None, "texto")                     # falta la columna
    nuevo = A.guardar_campo(config, -1, "Orden", "calculado", "numeracion", "texto")
    assert nuevo["tipo"] == "numero" and nuevo["id"] == "orden"
    vacio = A.guardar_campo(config, -1, "Observaciones", "vacio", "codigo", "texto")
    assert vacio["dato"] is None and A.describir_campo(config, vacio) == "No se llena"


def test_ordenar_campos(muestra, config):
    nombres = [c["nombre"] for c in config["campos"]]
    assert A.mover_campo(config, 0, 99)                                                    # «No.» al final
    assert [c["nombre"] for c in config["campos"]] == nombres[1:] + nombres[:1]
    assert not A.mover_campo(config, 2, 2)
    g = generar(muestra, config, ADMIN, 2022, 2022, logo=None)
    ws = openpyxl.load_workbook(g.ruta).worksheets[0]
    cab = next(r for r in ws.iter_rows(values_only=True) if nombres[1] in r)
    assert cab[0] == nombres[1] and cab[len(nombres) - 1] == nombres[0]


# ---------------------------------------------------------------- Reglas de cruce
def test_reglas_cambiadas_y_restablecer(config):
    assert not any(A.regla_cambiada(config, k) for k in A.CLAVES_REGLAS)
    config["reglas"]["r1_convenios_que_entran"]["vencidos"] = "con_o_sin_resultados"
    config["reglas"]["r4_fecha_fin"]["si_no_es_fecha"] = "revision"
    assert [k for k in A.CLAVES_REGLAS if A.regla_cambiada(config, k)] == ["r1_convenios_que_entran", "r4_fecha_fin"]
    A.restablecer_reglas(config, "r1_convenios_que_entran")
    assert not A.regla_cambiada(config, "r1_convenios_que_entran") and A.regla_cambiada(config, "r4_fecha_fin")
    A.restablecer_reglas(config)
    assert config["reglas"]["r4_fecha_fin"] == REGLAS_CONFIRMADAS["r4_fecha_fin"]
    config["reglas"]["r4_fecha_fin"]["si_no_es_fecha"] = "x"
    assert REGLAS_CONFIRMADAS["r4_fecha_fin"]["si_no_es_fecha"] == "inicio_mas_vigencia"   # se copió, no se compartió
    assert A.fecha_confirmada(config) == "23-nov-2026"


def test_opciones_de_reglas_que_ofrece_la_pantalla_las_aplica_el_motor(muestra, config):
    base = cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    config["reglas"]["r1_convenios_que_entran"]["vencidos"] = "con_o_sin_resultados"
    todos = cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    assert todos.convenios_en_cuadro > base.convenios_en_cuadro
    assert any(not f.total and not f.convenio.activo for f in todos.filas)
    config["reglas"]["r2_asignacion"]["preferido_movilidad"] = "ninguno"
    cruzar(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)                       # no falla


# ---------------------------------------------------------------- Ver cómo se aplican las reglas
def test_ver_como_se_aplican_sin_cambios(muestra, config):
    a = A.aplicar_reglas(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    assert a.cambiadas == [] and a.frase_efecto() is None
    assert all(x == y for _, x, y in a.efecto())
    decisiones = dict((n, t) for n, t, _ in a.decisiones())
    assert decisiones[3] == "2 movilidades · 3 actividades de internacionalización en casa"
    assert decisiones[2].startswith("5 registros asignados")
    ejemplos = a.ejemplos()
    assert ejemplos and all(e.regla in (1, 2, 4) for e in ejemplos)
    assert any("Movilidad 2022" in e.registro for e in ejemplos)


def test_ver_como_se_aplican_con_un_cambio(muestra, config):
    config["reglas"]["r1_convenios_que_entran"]["vencidos"] = "con_o_sin_resultados"
    a = A.aplicar_reglas(leer_carpeta(muestra, config, 2022, 2022), config, ADMIN)
    assert a.cambiadas == [1]
    (_, antes, despues), (_, sin_a, sin_d) = a.efecto()[:2]
    assert despues - antes == sin_d - sin_a > 0
    assert a.frase_efecto().startswith("Tu cambio en la regla 1 agrega ")
    assert a.decisiones()[0][2] is True
    assert any(e.regla == 1 and "vencidos entran con o sin resultados" in e.decision for e in a.ejemplos(12))
