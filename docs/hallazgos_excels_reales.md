# Hallazgos con los Excel reales (primera revisión)

Archivos revisados: cuadro maestro (Administración de Empresas, 2025-2), movilidad 2022 y
internacionalización en casa 2022-1 y 2022-2 (sede Pereira). Solo estructura; sin datos personales.

## Cuadro maestro (salida)
- Hoja única. Títulos y logo arriba (se ponen a mano). Encabezado de tabla en la fila 17 (internacionales) y 6 (nacionales).
- Columnas: No. · Institución · Breve objeto · Resultados concretos · Vigencia (años) · Activo · Nº de usuarios · No aplica.
- "Resultados concretos" es texto calculado: `AÑO` y, debajo, `- Tipo: cantidad`; si no hay nada, "Sin evidencia".
- Tipos vistos: Estudiante saliente, Estudiante entrante, Experto internacional, Internacionalización en casa.
- "Vigencia (años)" es una duración (5, 10…), no un rango de fechas. "Nº de usuarios" y "No aplica" están vacías.
- 93 filas = 67 instituciones; 21 instituciones tienen más de un convenio.

## Reportes: cómo varían (ya en solo 3 archivos de 2022)
- Fila de encabezado: 1 en movilidad e int. casa 2022-1; 2 en 2022-2 (hay una nota en la fila 1).
- Primera columna: A en unos, B en otros. Columnas corridas.
- Un encabezado fue sobrescrito con un nombre de universidad ("UNIVERSIDAD METODISTA ") en 2022-2.
- Hojas ocultas, macros (.xlsm), celdas combinadas, imágenes.
- Valores sucios: "N/A", "NA", vacío; fechas como texto ("20/05/222"); participantes como texto
  ("300 invitados y 25 ponencias"); roles y vínculos escritos de varias formas; instituciones con
  espacios o errores ("deSinaloa", "Istmo/del Istmo").
- Programa: una fila de movilidad puede traer varios programas separados por salto de línea.
- No hay código de convenio en los reportes: el cruce es por nombre de institución.

## Reglas inferidas del cuadro (por confirmar)
- Movilidad cuenta personas (1 por fila); int. casa cuenta actividades (filas), no participantes.
  Ej.: 10 filas "Clase espejo" 2022-1 con la misma institución → "2022 – Internacionalización en casa: 10".
- Tipo de persona sale de VINCULO SNIES (Experto Internacional, Estudiantes en el exterior/extranjeros…).
- Cuando una institución tiene dos convenios, parece que movilidad va al convenio de intercambio
  y int. casa al convenio marco/alianza.

## Prueba del mapeo automático (tools/prototipo_mapeo.py)
- Detecta fila de encabezado y mapea año, semestre, programa, institución, tipo de actividad,
  participantes y tipo de convenio en los 3 archivos, sin posiciones fijas.
- Coincidencia aproximada de nombres: da falsos positivos (Montreal→Continental, Carabobo→Caribe).
  Conclusión: solo se aplica automático lo exacto tras normalizar; lo parecido se propone y se confirma.

## Matriz de convenios (Excel 1)
- Hoja principal `CONV_INTERNACIONALES`: dos filas de encabezado (grupos en la fila 2, columnas en la 3), 328 convenios.
- Trae código de alianza, tipo (MARCO / ESPECÍFICO), fecha de inicio y fin, vigencia en años, estado (VIGENTE / VENCIDO / ANULADO).
- Los programas están como columnas "Programa - Sede" con APLICA / NO APLICA (ej.: "Administración de empresas - Pereira").
- Fecha de fin a veces es texto ("INDEFINIDO"), vacía o solo un año. Hojas ocultas: catálogos y homologaciones.
- "Breve objeto" del cuadro = "OBJETO DEL CONVENIO" de la matriz (93 de 93).
- Administración de Empresas Pereira: 157 convenios APLICA (88 vigentes, 69 vencidos) frente a 93 filas en el cuadro:
  el filtro real de qué entra al cuadro no se deduce de los datos (pregunta al jefe).
- Patrón visto: movilidad → convenio específico; IC → convenio marco; si falta uno, va al que exista.
- Preguntas pendientes para el jefe: documento "Cuadro maestro internacional automatizado: preguntas para definir las reglas".
