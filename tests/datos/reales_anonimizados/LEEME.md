# Excel reales anonimizados (datos de prueba)

Carpeta para las copias anonimizadas de los Excel reales de la Oficina de Relaciones Internacionales (sede Pereira,
año 2022). **Las copias no se suben al repositorio** (están en `.gitignore`): aunque no tienen nombres, correos ni
documentos, cada fila de movilidad conserva año, programa, institución y tipo de persona, y con eso alguien que
conozca la oficina podría reconocer a una persona. Viven solo en el equipo de quien las genera:

    python3 -I tools/anonimizar_reales.py <carpeta_con_los_originales> tests/datos/reales_anonimizados

La persona responsable del proyecto autorizó usar los reales para las pruebas (23-nov-2026). En GitHub las pruebas
usan la muestra inventada de `tests/muestra_sintetica.py`, que reproduce las mismas rarezas.

Archivos que crea el script:

| Archivo | Original |
|---|---|
| `MATRIZ CONVENIOS INTERNACIONAL VIGENTES.xlsx` | Matriz de convenios (328 convenios) |
| `CONSOLIDADO DE MOVILIDAD INTERNACIONAL 2022 Pereira.xlsm` | Consolidado de movilidad 2022 |
| `Reporte Internacionalización en casa 2022-1 Pereira.xlsx` | Reporte de internacionalización en casa 2022-1 |
| `Reporte Internacionalización en casa 2022-2 Pereira.xlsm` | Reporte de internacionalización en casa 2022-2 |
| `CM 2025-2 Administración de Empresas Pereira (ejemplo de salida).xlsx` | Cuadro maestro hecho a mano (sin datos de personas; solo se quitó el autor y el logo) |

## Qué se conserva

La estructura y las rarezas de los reales: hojas ocultas, filas de títulos y notas, encabezado en la fila 1, 2 o 3,
columnas corridas, un encabezado sobrescrito con el nombre de una universidad, celdas combinadas, valores como "N/A",
fechas como texto, participantes como texto ("300 invitados y 25 ponencias") y errores de captura (una descripción
en la columna de institución, una ciudad en la columna de país). Se conservan tal cual las columnas que el programa
usa o que no identifican a nadie: año, semestre, programa, sede, institución, país de destino, tipos, vigencia,
estado, fechas de los convenios y de las actividades, y las columnas APLICA / NO APLICA.

## Qué cambia

- Nombres, correos, documentos, teléfonos, cargos, descripciones, perfiles, comentarios y enlaces: `Dato ficticio …`,
  `personaNNNN@ejemplo.org`, `https://ejemplo.org/evidencia/N`.
- Valores en dinero y otros números de columnas no conservadas: 0.
- Fechas de la movilidad de cada persona: 1 de enero del mismo año. Ciudad y país de origen de la persona: ficticios.
- Se quitaron macros, tablas dinámicas, validaciones de datos, comentarios, hipervínculos, imágenes y autor
  (algunos traían correos y nombres incrustados). Los .xlsm siguen siendo libros .xlsm, sin macros.

## Verificación

El script comprueba que ningún texto de las columnas de personas del original ni ningún correo real aparezca en
ninguna parte del archivo (celdas, fórmulas, listas y atributos internos). Además, `tools/prototipo_cruce.py`
da el mismo resultado con estas copias que con los originales.

Las fórmulas se guardaron como valores, porque así las lee el programa.
