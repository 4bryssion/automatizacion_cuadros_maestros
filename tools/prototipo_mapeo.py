"""Demo: detectar fila de encabezados y mapear columnas a campos canónicos (solo estructura, sin datos personales)."""
import sys, re, unicodedata, difflib, openpyxl, warnings
warnings.filterwarnings("ignore")

def norm(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)|\*", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

# campo canónico -> sinónimos conocidos (editable por el usuario en Configuración)
CAMPOS = {
    "anio": ["año", "anio", "year", "ano"],
    "semestre": ["semestre", "periodo", "sem"],
    "programa": ["programa o dependencia", "nombre programa dependencia", "programa", "nombre programa"],
    "institucion": ["institucion de origen destino", "entidad organizacion institucion internacional vinculada", "institucion", "universidad"],
    "tipo_movilidad": ["tipo movilidad", "movilidad", "sentido"],
    "vinculo": ["vinculo snies", "rol", "tipo participantes"],
    "tipo_actividad": ["tipo de actividad", "actividad"],
    "n_participantes": ["no de participantes", "numero de participantes", "participantes"],
    "tipo_convenio": ["tipo de convenio", "convenio"],
}

def detectar_encabezado(ws, max_busqueda=15):
    mejor = (0, None)
    for r in range(1, max_busqueda + 1):
        celdas = [norm(c.value) for c in ws[r] if c.value not in (None, "")]
        textos = [t for t in celdas if t and not t.isdigit()]
        if len(textos) < 4:
            continue
        puntaje = sum(1 for t in textos if any(difflib.SequenceMatcher(None, t, s).ratio() > .8 or s in t for sins in CAMPOS.values() for s in sins))
        if puntaje > mejor[0]:
            mejor = (puntaje, r)
    return mejor[1]

def mapear(ws, fila):
    out = {}
    for c in ws[fila]:
        if c.value in (None, ""):
            continue
        h = norm(c.value)
        cand = []
        for campo, sins in CAMPOS.items():
            for s in sins:
                if h == s: cand.append((1.0, campo, "exacto"))
                elif h.startswith(s) and len(s) > 5: cand.append((.95, campo, "empieza igual"))
                else:
                    r = difflib.SequenceMatcher(None, h, s).ratio()
                    if r > .7: cand.append((r, campo, "parecido"))
        if cand:
            p, campo, how = max(cand)
            if campo not in out or p > out[campo][2]:   # se queda la mejor coincidencia, no la última
                out[campo] = (c.column_letter, str(c.value).strip()[:38], round(p, 2), how)
    return out

for f, hoja in [("56ee5752-CONSOLIDADO_DE_MOVILIDAD_INTERNACIONAL_2022_Pereira.xlsm", "BD GENERAL"),
                ("91bf4ded-Reporte_Internacionalizaci_n_en_casa_2022-1_Pereira.xlsx", "Hoja1"),
                ("6bf2af10-Reporte_Internacionalizaci_n_en_casa_2022-2_Pereira.xlsm", "BASE DE DATOS")]:
    ws = openpyxl.load_workbook("/mnt/user-data/uploads/" + f, data_only=True)[hoja]
    fila = detectar_encabezado(ws)
    print(f"\n{hoja}: encabezado detectado en la fila {fila}")
    for campo, (col, h, p, how) in mapear(ws, fila).items():
        print(f"   {campo:15} <- col {col:3} '{h}'  ({how}, {p})")
    faltan = [c for c in CAMPOS if c not in mapear(ws, fila)]
    print("   sin encontrar:", faltan)
