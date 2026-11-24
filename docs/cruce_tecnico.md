# Cruce y avisos de la revisión (técnico)

Código: `src/cuadro_maestro/cruce/`. Pruebas: `tests/test_cruce.py`. Entrada: la `Lectura` (paso anterior), la
configuración y el programa. Salida: `ResultadoCruce` con las filas del cuadro, los avisos de la revisión y las cifras
del resumen (archivos leídos, convenios en el cuadro, movilidades y actividades contadas). Es el paso 4 de la
generación y lo mismo que usa la vista previa.

## Convenios del programa (matriz)

1. Entran a evaluación las filas cuya columna del programa dice el valor de la regla 1 (APLICA). Si esa columna no es
   exacta, o falta alguna columna imprescindible de la matriz (institución, tipo, fecha de inicio, estado), no hay
   convenios: el aviso de la columna explica por qué.
2. **Fecha de inicio** no válida → aviso «Convenio sin fecha de inicio válida» y el convenio queda fuera.
3. **Fin:** si la fecha de fin es una fecha, su año; si fin < inicio → aviso «Fecha de fin anterior a la de inicio» y
   queda fuera. Si no es una fecha (INDEFINIDO, vacía, solo un año): año de inicio + vigencia en años (regla 4); sin
   vigencia → aviso «Convenio sin fecha de fin ni vigencia en años» y queda fuera.
4. **Activo** si el estado está en `valores_activo` (VIGENTE); No Activo si está en `valores_no_activo` (VENCIDO,
   ANULADO). Otro valor → No Activo y aviso «Estado no reconocido».
5. **Tipo:** empieza por «marco» → marco; por «específic» → específico; lo demás → otro.

## Cada fila de movilidad o de internacionalización en casa

Se usa un archivo solo si sus columnas imprescindibles son exactas (institución y programa; en movilidad también el
vínculo). Una columna «por confirmar» no se usa hasta confirmarla. Para cada fila, en este orden:

| Paso | Qué se mira | Si no se cumple |
|---|---|---|
| Sede | Igual a la del filtro (Pereira), si la columna existe | Se omite sin aviso |
| Programa | Alguno de los programas de la celda (uno por línea) es el elegido, directo o por equivalencia | Se omite; si se parece al elegido (≥ 90 %) y no es otro programa configurado → aviso «Programa parecido» |
| Año | El de la fila (o el del archivo si está vacío), dentro de la vigencia elegida | Se omite |
| Institución vacía | — | IC: se cuenta y se informa solo la cantidad (P11). Movilidad: aviso informativo |
| Tipo de persona | Movilidad: el vínculo está en algún tipo; IC: el tipo base | Aviso «Tipo de persona no reconocido» |
| Institución | Coincide (normalizada, con equivalencias) con un convenio del programa | Existe en la matriz pero sin convenio del programa → informativo. La fila dice «sin convenio» → informativo. Si no → «Institución sin coincidencia» con 3 sugerencias |
| Vigencia | Algún convenio de esa institución cubre el año (regla 2) | Informativo «sin convenio vigente en su año» |
| Asignación | Prefiere específico (movilidad) o marco (IC); si hay varios, el de inicio más reciente | — |

Se suma 1 por fila (regla 3). Los avisos de filas se **agrupan** por archivo y nombre, con la cantidad y las primeras filas.

## Qué convenios entran al cuadro (regla 1)

Activos: con o sin resultados. No activos (vencidos y anulados): solo si tuvieron resultados en la vigencia elegida
(o todos, si se cambia la regla). Orden alfabético por institución; si se repite, por fecha de inicio. Numeración de corrido.

«Resultados concretos»: cada año en una línea y debajo «- Tipo: cantidad», en el orden de Tipos de persona; sin nada,
«Sin evidencia» (formato del cuadro hecho a mano). Activo: «Activo» / «No Activo».

## Avisos

Cada aviso trae grupo (`excel`, `programa`, `informativo`), título, dónde (archivo, hoja, fila, institución; nunca datos
de personas), qué pasó, qué hacer, acciones (botones) y una **clave estable** para comparar antes y después de recargar.
Los avisos de la lectura que solo afectan a otros programas (la columna de otro programa) no se muestran.

## Comprobado con los Excel de 2022 (Administración de Empresas)

- Reproduce el cuadro hecho a mano para 2022: Universidad Continental, Experto internacional 1 en el específico (10 años)
  e Internacionalización en casa 10 en el marco (5 años).
- 157 convenios aplican; 88 entran. Las diferencias con las 93 filas del cuadro 2025-2 se explican porque la matriz es
  más reciente (renovaciones, convenios que ya vencieron sin resultados en 2022, uno que perdió la fecha de inicio) y
  porque solo hay reportes de 2022.
- Revisión: 1 convenio sin fecha de inicio, «Universidad Siglo 21» sin coincidencia, 1 movilidad declarada sin convenio
  y 3 actividades sin institución.
