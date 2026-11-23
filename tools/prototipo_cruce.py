"""Prueba de las reglas de negocio confirmadas (solo conteos, sin datos personales).
Uso: python3 -I prototipo_cruce.py <matriz.xlsx> <cuadro.xlsx> <movilidad.xlsm> <ic1.xlsx> <ic2.xlsm>
"""
import sys, re, unicodedata, collections, warnings, openpyxl
warnings.filterwarnings("ignore")
MATRIZ, CUADRO, MOV, IC1, IC2 = sys.argv[1:6]
PROGRAMA, SEDE, ANIO = "administracion de empresas", "pereira", 2022

def norm(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s); s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

# ---- matriz: convenios que APLICAN al programa (columna "Programa - Sede")
ws = openpyxl.load_workbook(MATRIZ, data_only=True)["CONV_INTERNACIONALES"]
H = {norm(c.value): c.column_letter for c in ws[3] if c.value}
col_prog = next(l for h, l in H.items() if h.startswith(PROGRAMA) and h.endswith(SEDE))
c = lambda nombre: next(l for h, l in H.items() if h.startswith(nombre))
convenios = []
for r in range(4, ws.max_row + 1):
    if not ws[f"B{r}"].value or ws[f"{col_prog}{r}"].value != "APLICA":
        continue
    ini, fin, vig = ws[f"{c('fecha de inicio')}{r}"].value, ws[f"{c('fecha de finalizacion')}{r}"].value, ws[f"{c('vigencia en anos')}{r}"].value
    a_ini = ini.year if hasattr(ini, "year") else None
    a_fin = fin.year if hasattr(fin, "year") else (a_ini + int(vig) if a_ini and vig else None)   # P3-B
    convenios.append(dict(inst=norm(ws[f"B{r}"].value), tipo=norm(ws[f"{c('tipo de convenio')}{r}"].value),
                          ini=a_ini, fin=a_fin, vig=int(vig) if vig else None, fila=r, ini_f=ini))

# ---- registros (solo estructura: año, programa, institución, vínculo)
VINCULO = {"estudiantes en el exterior": "Estudiante saliente", "estudiantes extranjeros": "Estudiante entrante",
           "experto internacional": "Experto internacional", "profesores en el exterior": "Docente saliente",
           "profesores extranjeros": "Docente entrante", "administrativo en el exterior": "Administrativo saliente",
           "administrativos en el exterior": "Administrativo saliente", "administrativo extranjero": "Administrativo entrante"}
registros, sin_inst = [], 0
mv = openpyxl.load_workbook(MOV, data_only=True)["BD GENERAL"]
for r in range(2, mv.max_row + 1):
    progs = [norm(p) for p in str(mv[f"J{r}"].value or "").split("\n")]
    if PROGRAMA in progs and mv[f"A{r}"].value == ANIO and norm(mv[f"H{r}"].value) == SEDE:
        registros.append(("mov", mv[f"A{r}"].value, norm(mv[f"R{r}"].value), VINCULO.get(norm(mv[f"C{r}"].value), "?" + norm(mv[f"C{r}"].value))))
for ruta, hoja, hdr, col in [(IC1, "Hoja1", 1, dict(a="A", p="K", i="R")), (IC2, "BASE DE DATOS", 2, dict(a="B", p="L", i="S"))]:
    w = openpyxl.load_workbook(ruta, data_only=True)[hoja]
    for r in range(hdr + 1, w.max_row + 1):
        progs = [norm(p) for p in str(w[f"{col['p']}{r}"].value or "").split("\n")]
        if PROGRAMA in progs and int(w[f"{col['a']}{r}"].value or 0) == ANIO:
            inst = norm(w[f"{col['i']}{r}"].value or "")
            if inst in ("", "n a", "na", "none"):
                sin_inst += 1; continue                       # P11: se omiten sin listar
            registros.append(("ic", ANIO, inst, "Internacionalización en casa"))

# ---- asignación a convenio: P7 (dentro de vigencia), P8 (mov→específico, IC→marco), P9 (más reciente)
cuentas, revision = collections.Counter(), []
for origen, anio, inst, tipo in registros:
    cand = [v for v in convenios if v["inst"] == inst and v["ini"] and v["fin"] and v["ini"] <= anio <= v["fin"]]
    pref = "especifico" if origen == "mov" else "marco"
    elegidos = [v for v in cand if v["tipo"] == pref] or cand
    if not elegidos:
        revision.append((origen, inst, tipo, "sin convenio vigente en ese año")); continue
    mejor = max(elegidos, key=lambda v: v["ini_f"])
    cuentas[(mejor["inst"], mejor["vig"], mejor["tipo"], anio, tipo)] += 1

# ---- comparar con el cuadro de ejemplo (solo líneas del año evaluado)
cm = openpyxl.load_workbook(CUADRO, data_only=True).worksheets[0]
esperado = collections.Counter()
for r in range(18, 111):
    txt, anio_actual = str(cm.cell(r, 4).value or ""), None
    for linea in txt.split("\n"):
        linea = linea.strip()
        if re.fullmatch(r"\d{4}", linea): anio_actual = int(linea)
        elif ":" in linea and anio_actual == ANIO:
            t, n = linea.lstrip("- ").rsplit(":", 1)
            t = {"Esxperto internacional": "Experto internacional"}.get(t.strip(), t.strip())
            esperado[(norm(cm.cell(r, 2).value), int(cm.cell(r, 5).value), anio_actual, t)] += int(n)
obtenido = collections.Counter()
for (inst, vig, tipo_c, anio, tipo), n in cuentas.items(): obtenido[(inst, vig, anio, tipo)] += n
print(f"Año {ANIO}: {len(registros)} registros del programa (+{sin_inst} IC sin institución omitidas)")
print("Calculado por las reglas :", dict(obtenido))
print("Cuadro de ejemplo (2022) :", dict(esperado))
print("COINCIDE" if obtenido == esperado else "DIFERENCIAS: faltan %s | sobran %s" % (dict(esperado - obtenido), dict(obtenido - esperado)))
print("A revisión:", revision)
