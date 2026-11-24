# Reglas de negocio confirmadas

Decididas por la jefatura de la Oficina de Relaciones Internacionales (23-nov-2026) a partir de las
16 preguntas del documento "Cuadro maestro internacional automatizado: preguntas para definir las reglas".
P15 se confirmó el 23-nov-2026: no hay restricciones para procesar los reportes con el programa.

## Qué convenios entran al cuadro (P1 a P3)
| Regla | Decisión | Cómo la aplica el programa |
|---|---|---|
| P1 | Entran los convenios que **aplican claramente** al programa (columna "Programa - Pereira" de la matriz = APLICA). Los **vigentes** entran con o sin resultados; los **vencidos** solo si tuvieron resultados en su momento. | Se calculan primero los resultados y después se descartan los vencidos sin resultados. |
| P2 | "Activo" / "No activo" sale de la columna ESTADO de la matriz el día que se genera el cuadro. | VIGENTE = Activo; VENCIDO o ANULADO = No activo. |
| P3 | Si la fecha de fin no es una fecha (INDEFINIDO, vacía), se usa "Vigencia en años" desde la fecha de inicio. | Año fin = año de inicio + vigencia en años. Sin inicio válido: va a la revisión. |

## Cómo se cuenta (P4 a P7)
| Regla | Decisión |
|---|---|
| P4 | Movilidad cuenta **movilidades** (una fila = 1). Una persona que viaja dos veces suma 2. |
| P5 | Internacionalización en casa cuenta **actividades** (una fila = 1), no participantes. |
| P6 | Se incluyen docentes y administrativos: Docente saliente, Docente entrante, Administrativo saliente, Administrativo entrante, además de Estudiante saliente, Estudiante entrante, Experto internacional e Internacionalización en casa. |
| P7 | Un registro cuenta solo si su año está dentro de los años de vigencia del convenio (ambos extremos incluidos). Los casos del cuadro manual fuera de vigencia se consideran errores. |

El tipo de persona de la movilidad sale de la columna "Vínculo SNIES" del consolidado.

## A qué convenio se asigna (P8 a P11)
Para cada registro, en este orden:
1. Candidatos: convenios del programa cuya institución coincide (nombre normalizado) y cuya vigencia cubre el año del registro.
2. Preferencia por tipo: movilidad va al convenio **específico**, internacionalización en casa al **marco**.
3. Si no hay del tipo preferido, va al que exista (P8).
4. Si hay varios del mismo tipo, va al **de inicio más reciente** (P9).
5. Sin candidatos (sin convenio o institución fuera del cuadro): se omite y se lista en el informe de revisión (P10).
6. Actividades de internacionalización en casa **sin institución**: se omiten y no se listan (P11). El resumen solo muestra una línea de conteo ("3 actividades sin institución omitidas"), sin detallarlas. Las filas con varios programas cuentan para cada programa listado.

## Presentación (P12 a P14)
- "Nº de usuarios" y "No aplica" se dejan vacías; las llena cada programa a mano (P12).
- Las filas se ordenan alfabéticamente por institución y se numeran de corrido; la sección de convenios nacionales queda vacía (P13).
- Cada cuadro es de **un programa académico, solo sede Pereira**; no se usa información de otras sedes (P14).
- "Breve objeto" es copia del "Objeto del convenio" de la matriz; "Vigencia (años)" sale de "Vigencia en años".

## IA externa (P16)
Se permite usar Gemini solo con títulos de columnas y nombres de instituciones, nunca con filas de datos ni
datos de personas. El programa debe funcionar completo sin IA.
Decisión de diseño: el programa **no se conecta** a Gemini. Prepara el mensaje, la persona lo pega en Gemini en el
navegador y pega la respuesta de vuelta; un modal explica los 4 pasos con ilustraciones. No hace falta clave de acceso
ni conexión desde el programa. Las sugerencias nunca se aplican sin confirmación.

## Programas y listas editables
- La lista de programas sale de la matriz: 25 columnas "Programa - Pereira". Se pueden listar, modificar, crear y eliminar.
- Lo mismo aplica a campos del cuadro, equivalencias de instituciones y de programas, tipos de persona y reglas de cruce:
  cada lista se administra en un modal con una fila por elemento (editar y eliminar dentro de la fila) y un botón Crear.
- Los nombres distintos entre matriz y reportes se resuelven con la tabla de equivalencias, que se confirma una vez.
- Los convenios sin fecha de inicio válida van al informe de revisión.

## Verificación

El motor de cruce (`src/cuadro_maestro/cruce/`, detalle en [cruce_tecnico.md](cruce_tecnico.md)) aplica estas reglas y
reproduce el mismo resultado de 2022 con los archivos reales. Antes se había comprobado con el prototipo:

`tools/prototipo_cruce.py` aplica estas reglas a los archivos de 2022 y reproduce exactamente lo que dice el
cuadro de ejemplo para ese año (Universidad Continental: Experto internacional 1 en el convenio específico
e Internacionalización en casa 10 en el marco). La Universidad Siglo 21 y la Academia de Defensa Militar
Conjunta quedan en la revisión.

## Casos límite detectados (por decidir)
- 6 de 328 convenios no tienen fecha de inicio válida: no se pueden ubicar en años (van a la revisión).
- Los nombres de programa no siempre coinciden entre la matriz y los reportes (por ejemplo "Ingeniería Industrial Distancia"
  frente a "Ingeniería Industrial"): se resuelven con equivalencias.
- Los reportes de movilidad traen un tipo de convenio "RED" que no existe en la matriz (solo marco y específico).
