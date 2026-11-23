# Lectura de los Excel (técnico)

Código: `src/cuadro_maestro/lectura/`. Pruebas: `tests/test_lectura.py`. Entrada: carpeta, configuración y vigencia
(año inicial y final). Salida: un objeto `Lectura` con lo esperado, lo leído, los errores y los avisos. Corresponde a los
pasos 1 a 3 de la generación y es lo mismo que usan la vista previa y «Probar lectura de la carpeta».

La lectura **no depende del programa elegido**: deja las filas tal como vienen, con su número de fila de Excel, y el
cruce aplica después los filtros (programa, sede, vacíos). Cambiar de programa no obliga a volver a leer.

## 1. Qué archivos se buscan (`archivos.py`)

- Solo la carpeta elegida, sin subcarpetas (así `Cuadros generados` nunca se lee). Se ignoran `~$…` y archivos ocultos.
- Cada fuente reconoce sus archivos por el nombre normalizado: debe **contener** todos los textos de `archivo.contiene`
  y no tener ninguna palabra de `archivo.excluye`. La matriz: contiene «convenios» y excluye «cuadro» y «cm» (el cuadro
  hecho a mano se llama `CM_…_Convenios.xlsx`).
- Año y semestre salen del nombre con `patron_anio` y `patron_semestre`. Según tenga uno, otro o ninguno, la fuente
  pide un archivo por semestre (internacionalización en casa), por año (movilidad) o uno solo (matriz).
- Para cada hueco de la vigencia: si no hay archivo → aviso `falta_archivo` (o `falta_matriz`, que bloquea); si hay
  varios → se usa el **modificado más recientemente** y se avisa `archivos_repetidos`; si existe `~$nombre` → aviso
  informativo `abierto_en_excel`. Un archivo de la fuente sin año o semestre en el nombre → `archivo_sin_periodo`.

## 2. Abrir (`libro.py`)

El archivo se lee entero a memoria y se cierra al instante (en Windows, tenerlo abierto molestaría a Excel). Luego:

| Qué se encuentra | Causa | Efecto |
|---|---|---|
| Permiso denegado o archivo bloqueado (WinError 32/33) | `en_uso` | Error: detiene la generación |
| Contenedor de Office con flujo `EncryptedPackage` | `con_contrasena` | Error |
| Contenedor de Office sin cifrar (un `.xls` antiguo), vacío, no es ZIP, ZIP roto o cualquier falla de openpyxl | `danado` | Error |

Los textos de «Qué pasó» y «Qué hacer» están en `ErrorLectura` y son los del mockup 43. Todos los errores se recogen
y se devuelven juntos. Se abre con `read_only` y `data_only` (valores, no fórmulas).

## 3. Hoja, fila de encabezados y columnas (`encabezados.py`)

- **Hoja:** la preferida de la fuente si existe; si no, la hoja visible cuyos encabezados reconocen más datos.
- **Fila de encabezados:** entre las 15 primeras, la que reconoce más datos por coincidencia exacta de sinónimos
  (o la fila fija si la detección automática está apagada en Fuentes de datos).
- **Columna de cada dato:** primero lo exacto (incluida la columna que eligió la persona, `elegida`); después lo
  parecido (empieza igual, la contiene o se parece en un 75 % o más) queda `por_confirmar` con su puntaje; lo demás,
  `sin_identificar`. Una columna no se asigna a dos datos. Solo lo exacto se usa sin preguntar.
- **Programas (solo la matriz):** la columna de cada programa configurado, exacta o parecida (85 %) entre las de la
  sede. Las columnas de la sede que no son de ningún programa dan el aviso `programa_nuevo_en_matriz` (botón
  «Abrir Programas» en la revisión).

## 4. Filas (`lector.py`)

Cada fila con algún dato es un `Registro` con su número de fila de Excel y los valores de los datos (y, en la matriz,
el valor APLICA / NO APLICA de cada programa). Las conversiones tolerantes (años 2022 / 2022.0 / "2022", fechas como
texto, vacíos como «N/A», listas con saltos de línea) están en `valores.py` y las usa el cruce.

La lectura se puede cancelar en cualquier momento (`cancelado`) y avisa su avance (`al_avanzar`) para el modal de progreso.

## Comprobado con los Excel de 2022

Matriz: 328 convenios, las 8 columnas y los 25 programas exactos. Movilidad: 117 filas, encabezado en la fila 1.
Internacionalización en casa 2022-1: 75 filas, fila 1; 2022-2: 68 filas, fila 2, primera columna B. Ningún aviso.
Las columnas encontradas son las mismas que el prototipo tenía fijas a mano.
