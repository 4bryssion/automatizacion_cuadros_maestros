"""Exportar e importar la configuración (mockup 23)."""
import json

import pytest

from cuadro_maestro import ajustes as A
from cuadro_maestro.configuracion import AlmacenConfiguracion
from cuadro_maestro.configuracion import intercambio as X
from cuadro_maestro.configuracion.almacen import ANTES_DE_IMPORTAR


@pytest.fixture
def almacen(tmp_path):
    a = AlmacenConfiguracion(tmp_path / "u", tmp_path / "p")
    a.cargar()
    return a


def test_exportar_no_sobrescribe(almacen, tmp_path):
    destino = tmp_path / "exportadas"
    destino.mkdir()
    r1 = X.exportar(almacen.actual, destino, "Config")
    r2 = X.exportar(almacen.actual, destino, "Config.json")
    assert (r1.name, r2.name) == ("Config.json", "Config (2).json")
    assert X.leer(r1)["programas"] == almacen.actual["programas"]
    assert X.nombre_sugerido().startswith("Configuracion_CuadroMaestro_20")


def test_archivos_que_no_se_pueden_importar(tmp_path):
    malo = tmp_path / "x.json"
    malo.write_text("no es json", encoding="utf-8")
    with pytest.raises(X.ErrorImportar, match="no es una configuración"):
        X.leer(malo)
    malo.write_text(json.dumps({"formato": "otra-cosa"}), encoding="utf-8")
    with pytest.raises(X.ErrorImportar, match="no es una configuración"):
        X.leer(malo)
    malo.write_text(json.dumps({"formato": "cuadro-maestro-configuracion", "version_esquema": 99}), encoding="utf-8")
    with pytest.raises(X.ErrorImportar, match="versión más nueva"):
        X.leer(malo)
    malo.write_text(json.dumps({"formato": "cuadro-maestro-configuracion", "version_esquema": 1}), encoding="utf-8")
    with pytest.raises(X.ErrorImportar, match="incompleto o dañado"):
        X.leer(malo)
    with pytest.raises(X.ErrorImportar, match="No se pudo abrir"):
        X.leer(tmp_path / "no existe.json")


def _otra(tmp_path):
    """Otro equipo: un campo País, dos equivalencias, un valor de tipo nuevo y una regla distinta."""
    b = AlmacenConfiguracion(tmp_path / "u2", tmp_path / "p2")
    b.cargar()
    cfg = json.loads(json.dumps(b.actual))
    A.guardar_campo(cfg, -1, "País", "matriz", "enc:PAÍS", "texto")
    cfg["equivalencias_instituciones"] += [{"como_aparece": "U. Ficticia", "es": "UNIVERSIDAD FICTICIA", "origen": "tu"},
                                          {"como_aparece": "Inst. Sur", "es": "INSTITUTO DEL SUR", "origen": "gemini"}]
    cfg["tipos_persona"][0]["valores"].append("pasante internacional")
    cfg["reglas"]["r1_convenios_que_entran"]["vencidos"] = "con_o_sin_resultados"
    del cfg["programas"][0]
    b.guardar(cfg)
    return b.actual


def test_comparar_combinar_y_reemplazar(almacen, tmp_path):
    otro = _otra(tmp_path)
    cambios = {n: c for n, _, _, c in X.comparar(almacen.actual, otro)}
    assert cambios == {"Programas": "−1", "Campos del cuadro": "+1", "Fuentes de datos": "1 distinta",
                       "Equivalencias": "+2", "Tipos de persona": "1 distinta", "Reglas de cruce": "1 distinta"}
    mio = json.loads(json.dumps(almacen.actual))
    mio["equivalencias_instituciones"].append({"como_aparece": "u. ficticia", "es": "OTRA", "origen": "tu"})
    combinada = X.preparar(mio, otro, X.COMBINAR)
    assert len(combinada["programas"]) == 25                               # no quita los tuyos
    assert combinada["campos"][-1]["nombre"] == "País"
    assert "col-pais" in A.fuente(combinada, "matriz")["columnas"]        # con la columna que necesita
    eq = {e["como_aparece"]: e["es"] for e in combinada["equivalencias_instituciones"]}
    assert eq == {"u. ficticia": "OTRA", "Inst. Sur": "INSTITUTO DEL SUR"}  # la tuya gana
    assert "pasante internacional" in combinada["tipos_persona"][0]["valores"]
    assert not A.regla_cambiada(combinada, "r1_convenios_que_entran")       # las reglas no se tocan
    reemplazada = X.preparar(mio, otro, X.REEMPLAZAR)
    assert len(reemplazada["programas"]) == 24 and A.regla_cambiada(reemplazada, "r1_convenios_que_entran")
    # importar deja una copia «Antes de importar»
    antes = almacen.actual["revision"]
    doc = almacen.importar(combinada)
    assert doc["revision"] == antes + 1 and doc["campos"][-1]["nombre"] == "País"
    assert any(c.motivo == ANTES_DE_IMPORTAR for c in almacen.copias_de_seguridad())


def test_un_campo_de_tipo_fecha_se_puede_guardar(almacen):
    """Campos ofrece «Fecha»: la configuración con ese tipo tiene que ser válida (si no, no se guardaría)."""
    cfg = json.loads(json.dumps(almacen.actual))
    A.guardar_campo(cfg, -1, "Inicio", "matriz", "fecha_inicio", "fecha")
    assert almacen.guardar(cfg)["campos"][-1]["tipo"] == "fecha"
