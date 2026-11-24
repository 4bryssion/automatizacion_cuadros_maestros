"""Pruebas del guardado doble de la configuración. Solo datos de configuración; ningún dato de personas."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from cuadro_maestro.configuracion import almacen as A
from cuadro_maestro.configuracion import esquema
from cuadro_maestro.configuracion.almacen import AlmacenConfiguracion, ErrorDeGuardado
from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial


class Reloj:
    """Reloj falso que avanza un segundo en cada lectura."""

    def __init__(self, inicio=datetime(2026, 11, 23, 15, 0, tzinfo=timezone.utc)):
        self.t = inicio

    def __call__(self):
        self.t += timedelta(seconds=1)
        return self.t


@pytest.fixture
def carpetas(tmp_path):
    return tmp_path / "AppData", tmp_path / "Portable" / "Configuración"


@pytest.fixture
def reloj():
    return Reloj()


def nuevo(carpetas, reloj, **kw):
    return AlmacenConfiguracion(*carpetas, reloj=reloj, **kw)


def leer(carpeta):
    return json.loads((carpeta / A.NOMBRE_ARCHIVO).read_text(encoding="utf-8"))


def con_cambio(doc, nombre="Institución X"):
    d = esquema.sin_metadatos(doc)
    d["equivalencias_instituciones"] = [{"como_aparece": nombre, "es": "Institución Y", "origen": "tu"}]
    return d


# ---------------------------------------------------------------- valores iniciales y esquema
def test_configuracion_inicial_es_valida_y_trae_los_25_programas(carpetas, reloj):
    r = nuevo(carpetas, reloj).cargar()
    assert esquema.validar(r.configuracion) == []
    assert len(r.configuracion["programas"]) == 25
    assert {c["id"] for c in r.configuracion["campos"] if c["base"]} == {"institucion", "resultados", "vigencia", "activo"}
    assert [t["nombre"] for t in r.configuracion["tipos_persona"] if t["base"]] == ["Internacionalización en casa"]
    assert r.configuracion["reglas"]["r1_convenios_que_entran"]["vencidos"] == "solo_con_resultados"


def test_validar_detecta_problemas_concretos():
    doc = {"formato": esquema.FORMATO, "version_esquema": 1, "guardado_en": "x", "revision": 1,
           **configuracion_inicial()}
    doc["campos"][0]["fuente"] = "otra"
    doc["programas"].append(dict(doc["programas"][0]))
    problemas = esquema.validar(doc)
    assert any("fuente «otra»" in p for p in problemas)
    assert any("repetido" in p for p in problemas)
    assert esquema.validar([]) == ["El archivo no contiene una configuración."]


# ---------------------------------------------------------------- primera vez y guardado
def test_primera_vez_guarda_en_los_dos_lugares_sin_aviso(carpetas, reloj):
    r = nuevo(carpetas, reloj).cargar()
    assert r.situacion == A.PRIMERA_VEZ
    assert leer(carpetas[0]) == leer(carpetas[1]) == r.configuracion
    assert r.configuracion["revision"] == 1


def test_guardar_escribe_en_ambos_y_hace_una_copia_automatica_por_sesion(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    a.cargar()
    a2 = nuevo(carpetas, reloj)                     # nueva sesión
    doc = a2.cargar().configuracion
    d1 = a2.guardar(con_cambio(doc, "A"))
    d2 = a2.guardar(con_cambio(d1, "B"))
    assert d2["revision"] == 3
    assert leer(carpetas[0]) == leer(carpetas[1]) == d2
    copias = a2.copias_de_seguridad()
    assert [c.motivo for c in copias] == [A.AUTOMATICA]          # solo una en toda la sesión
    assert copias[0].configuracion["revision"] == 1               # guarda lo que había antes del cambio
    assert not list(carpetas[0].glob(".*.tmp"))


def test_guardar_rechaza_una_configuracion_invalida(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    doc = esquema.sin_metadatos(a.cargar().configuracion)
    doc["campos"][0]["tipo"] = "moneda"
    with pytest.raises(ValueError):
        a.guardar(doc)


# ---------------------------------------------------------------- al abrir
def test_reabrir_sin_cambios_no_avisa(carpetas, reloj):
    nuevo(carpetas, reloj).cargar()
    r = nuevo(carpetas, reloj).cargar()
    assert r.situacion == A.NORMAL and r.usada in (A.USUARIO, A.PROGRAMA)


def test_falta_la_copia_del_usuario_se_restaura_desde_la_del_programa(carpetas, reloj):
    nuevo(carpetas, reloj).cargar()
    (carpetas[0] / A.NOMBRE_ARCHIVO).unlink()            # p. ej. el equipo borró el perfil
    r = nuevo(carpetas, reloj).cargar()
    assert r.situacion == A.RESTAURADA and r.usada == A.PROGRAMA
    assert r.lugares[0].estado == "falta" and r.lugares[0].restaurada
    assert leer(carpetas[0]) == leer(carpetas[1])


def test_copia_danada_se_guarda_aparte_una_sola_vez_y_se_restaura(carpetas, reloj):
    nuevo(carpetas, reloj).cargar()
    (carpetas[0] / A.NOMBRE_ARCHIVO).write_text('{"formato": "cuadro-maes', encoding="utf-8")
    r = nuevo(carpetas, reloj).cargar()
    assert r.situacion == A.RESTAURADA
    assert r.lugares[0].estado == "danada"
    danadas = [c for c in r.copias if c.motivo == A.DANADA]
    assert len(danadas) == 1 and not danadas[0].restaurable
    # Si vuelve a dañarse con el mismo contenido no se acumulan copias repetidas.
    (carpetas[0] / A.NOMBRE_ARCHIVO).write_text('{"formato": "cuadro-maes', encoding="utf-8")
    r2 = nuevo(carpetas, reloj).cargar()
    assert len([c for c in r2.copias if c.motivo == A.DANADA]) == 1


def test_dos_copias_validas_distintas_gana_la_mas_reciente_y_avisa(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    a.cargar()
    viejo = leer(carpetas[0])
    a.guardar(con_cambio(viejo, "Nueva"))
    (carpetas[0] / A.NOMBRE_ARCHIVO).write_text(json.dumps(viejo), encoding="utf-8")   # AppData quedó atrás
    r = nuevo(carpetas, reloj).cargar()
    assert r.situacion == A.DISTINTAS and r.usada == A.PROGRAMA
    assert r.configuracion["equivalencias_instituciones"][0]["como_aparece"] == "Nueva"
    assert leer(carpetas[0]) == leer(carpetas[1])
    descartada = [c for c in r.copias if c.motivo == A.DESCARTADA]
    assert len(descartada) == 1 and descartada[0].restaurable
    assert descartada[0].configuracion["equivalencias_instituciones"] == []


def test_gana_la_fecha_guardada_dentro_y_no_la_del_archivo(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    a.cargar()
    viejo = leer(carpetas[1])
    a.guardar(con_cambio(viejo, "Nueva"))
    # Se reescribe la copia vieja en el programa DESPUÉS: su fecha de Windows es la más nueva, la interna no.
    (carpetas[1] / A.NOMBRE_ARCHIVO).write_text(json.dumps(viejo), encoding="utf-8")
    r = nuevo(carpetas, reloj).cargar()
    assert r.usada == A.USUARIO
    assert r.configuracion["equivalencias_instituciones"][0]["como_aparece"] == "Nueva"


def test_ninguna_copia_legible_no_sobrescribe_y_permite_restaurar(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    a.cargar()
    a.guardar(con_cambio(leer(carpetas[0]), "Guardada"))      # deja una copia automática restaurable
    for c in carpetas:
        (c / A.NOMBRE_ARCHIVO).write_bytes(b"\xff\xfe basura")
    b = nuevo(carpetas, reloj)
    r = b.cargar()
    assert r.situacion == A.NO_ENCONTRADA
    assert (carpetas[0] / A.NOMBRE_ARCHIVO).read_bytes() == b"\xff\xfe basura"   # nada se tocó todavía
    restaurables = [c for c in r.copias if c.restaurable]
    assert restaurables
    doc = b.restaurar(restaurables[0])
    assert leer(carpetas[0]) == leer(carpetas[1]) == doc


def test_ninguna_copia_legible_y_sin_copias_restaurables_solo_informa(carpetas, reloj):
    for c in carpetas:
        c.mkdir(parents=True)
        (c / A.NOMBRE_ARCHIVO).write_text("no es json", encoding="utf-8")
    b = nuevo(carpetas, reloj)
    r = b.cargar()
    assert r.situacion == A.NO_ENCONTRADA
    assert not any(c.restaurable for c in r.copias)
    doc = b.seguir_con_la_inicial()
    assert len(doc["programas"]) == 25 and leer(carpetas[1]) == doc


def test_version_mas_nueva_se_guarda_aparte_antes_de_sobrescribir(carpetas, reloj):
    nuevo(carpetas, reloj).cargar()
    futura = leer(carpetas[0]) | {"version_esquema": 99}
    (carpetas[0] / A.NOMBRE_ARCHIVO).write_text(json.dumps(futura), encoding="utf-8")
    r = nuevo(carpetas, reloj).cargar()
    assert r.lugares[0].estado == "version_nueva"
    assert [c.motivo for c in r.copias] == [A.VERSION_NUEVA]
    assert "versión 99" in r.lugares[0].detalle


def test_carpeta_del_programa_sin_permiso_usa_solo_la_del_usuario(tmp_path, reloj):
    bloqueo = tmp_path / "disco_protegido"
    bloqueo.write_text("")                          # un archivo: no se pueden crear carpetas dentro
    a = AlmacenConfiguracion(tmp_path / "AppData", bloqueo / "Configuración", reloj=reloj)
    r = a.cargar()
    assert r.solo_usuario and r.situacion == A.PRIMERA_VEZ
    doc = a.guardar(con_cambio(r.configuracion))
    assert leer(tmp_path / "AppData") == doc
    r2 = AlmacenConfiguracion(tmp_path / "AppData", bloqueo / "Configuración", reloj=reloj).cargar()
    assert r2.situacion == A.NORMAL and r2.solo_usuario


def test_sin_ningun_lugar_escribible_falla_con_mensaje(tmp_path, reloj):
    bloqueo = tmp_path / "f"
    bloqueo.write_text("")
    with pytest.raises(ErrorDeGuardado):
        AlmacenConfiguracion(bloqueo / "a", bloqueo / "b", reloj=reloj).cargar()


# ---------------------------------------------------------------- copias de seguridad
def test_se_conservan_solo_las_ultimas_10_copias_en_cada_lugar(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    a.cargar()
    for _ in range(13):
        a.crear_copia()
    for c in carpetas:
        assert len(list((c / A.CARPETA_COPIAS).glob("*.json"))) == 10
    assert len(a.copias_de_seguridad()) == 10


def test_restaurar_guarda_antes_la_configuracion_actual(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    a.cargar()
    copia = a.crear_copia()
    a.guardar(con_cambio(a.actual, "Después"))
    a.restaurar(copia)
    motivos = [c.motivo for c in a.copias_de_seguridad()]
    assert motivos[0] == A.ANTES_DE_RESTAURAR
    assert a.actual["equivalencias_instituciones"] == []
    antes = a.copias_de_seguridad()[0].configuracion
    assert antes["equivalencias_instituciones"][0]["como_aparece"] == "Después"


def test_copias_se_leen_desde_cualquiera_de_los_dos_lugares(carpetas, reloj):
    a = nuevo(carpetas, reloj)
    a.cargar()
    a.crear_copia()
    import shutil
    shutil.rmtree(carpetas[0] / A.CARPETA_COPIAS)          # el perfil perdió sus copias
    assert len(nuevo(carpetas, reloj).copias_de_seguridad()) == 1


def test_la_configuracion_inicial_no_comparte_listas():
    """Cambiar una configuración no puede cambiar la inicial (los valores de un tipo eran la misma lista)."""
    from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
    a = configuracion_inicial()
    a["tipos_persona"][0]["valores"].append("x")
    a["fuentes"][0]["columnas"]["institucion"]["sinonimos"].append("x")
    b = configuracion_inicial()
    assert "x" not in b["tipos_persona"][0]["valores"]
    assert "x" not in b["fuentes"][0]["columnas"]["institucion"]["sinonimos"]
