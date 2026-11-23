# Pantalla "Ver revisión"

Boceto v0.6. Imágenes generadas con `tools/boceto_revision.py`.

## Para qué sirve

Después de generar el cuadro, el programa lista lo que **no pudo cruzar o dejó dudoso**. La pantalla tiene que
dejar claro tres cosas, sin conocer el programa:

1. Qué pasó.
2. Qué hacer, y **dónde** hacerlo: en el Excel o dentro del programa.
3. Cómo ver el resultado de la corrección: **recargar**.

## Flujo de trabajo

1. Leer el aviso.
2. Corregirlo:
   - **En el Excel:** editar el archivo, guardarlo y **cerrarlo**.
   - **En el programa:** elegir o indicar la opción correcta (equivalencias, Fuentes de datos).
3. Pulsar **Recargar archivos**. El programa vuelve a leer la carpeta y actualiza la lista.

## Tres grupos de avisos

Cada aviso pertenece a un grupo según **dónde se arregla**. Cada grupo tiene color, título y una frase que lo explica.

| Grupo | Color | Dónde se arregla | Ejemplos |
|---|---|---|---|
| Corrige el Excel y recarga | Magenta | Fuera del programa, en el Excel | Convenio sin fecha de inicio válida; falta el archivo de un año; fecha de fin anterior a la de inicio |
| Resuélvelo aquí en el programa | Naranja | Dentro del programa, sin tocar el Excel | Institución sin coincidencia; columna sin identificar |
| Solo informativo | Gris | No necesita acción | Movilidades sin convenio vigente en su año; actividades sin institución omitidas (solo el conteo) |

## Estructura de cada aviso

Todas las tarjetas tienen la misma forma, para que se lean igual:

- **Título** corto y concreto.
- **Dónde:** archivo, hoja y fila, o carpeta. Nunca nombres, documentos ni correos de personas.
- **Qué pasó:** una o dos frases, con la consecuencia (por ejemplo, "quedó fuera del cuadro").
- **Qué hacer:** pasos concretos. Termina con "pulsa Recargar archivos" cuando el aviso se corrige en el Excel.
- **Botones** de acción cuando existen: Abrir el Excel, Abrir carpeta, Elegir institución…, Preguntar a Gemini,
  Abrir Fuentes de datos.

## Recargar archivos

| Pregunta | Respuesta |
|---|---|
| ¿Qué hace? | Vuelve a leer todos los archivos de la carpeta y actualiza la lista de avisos. |
| ¿Modifica mis Excel? | No. |
| ¿Cambia el cuadro ya generado? | No. El cuadro anterior queda igual. |
| ¿Cómo se incluyen las correcciones en el cuadro? | Con **Generar cuadro de nuevo**, que pasa por la alerta de confirmación y crea un **archivo nuevo**. |
| ¿Qué pasa si el Excel sigue abierto? | El programa puede no ver los cambios. Por eso la barra inferior avisa: guarda y cierra los Excel antes de recargar. |

Decisión de diseño: separar *recargar* (solo mira) de *generar* (crea un archivo) evita sobrescribir un cuadro
entregado por accidente.

## Pantalla

- **Fijo arriba:** encabezado, volver al cuadro maestro, contexto (programa, vigencia, hora de generación),
  los tres pasos (Lee el aviso → Corrígelo → Recarga) y el resumen de avisos por grupo.
- **Con desplazamiento:** los avisos agrupados.
- **Fijo abajo:** advertencia de guardar y cerrar los Excel, hora de la última lectura, cantidad de archivos leídos,
  y los botones.

Los botones cambian de prioridad según el momento:

| Momento | Botón principal | Botón secundario |
|---|---|---|
| Antes de recargar | Recargar archivos | Generar cuadro de nuevo |
| Después de recargar, con cambios | Generar cuadro de nuevo | Recargar archivos |

## Después de recargar

- Aparece una franja con el resultado: "Antes 6 avisos, ahora 5" y tres contadores: **resueltos**, **siguen**, **nuevo**.
- Los avisos resueltos se agrupan arriba, en una caja verde, con lo que se logró.
- Cada aviso que sigue lleva una marca: **Sigue pendiente** (naranja), **Sin cambios** (gris) o **Nuevo** (magenta).
  Un aviso nuevo puede aparecer por una corrección: en el ejemplo, la fecha que se escribió quedó posterior a la de fin.
- La barra inferior explica que el cuadro anterior no cambió y que hay que generar de nuevo.

## Imágenes

| Archivo | Qué muestra |
|---|---|
| `revision_antes_arriba.png` | Primera vista, con los avisos que se corrigen en el Excel |
| `revision_antes_abajo.png` | Final de la lista: avisos del programa e informativos |
| `revision_despues.png` | Estado después de recargar: resueltos, pendientes y nuevo |

## Por definir

- Texto exacto de cada aviso para los casos que aparezcan con datos reales.
- Modal "Elegir institución…" (lista con búsqueda de las instituciones de la matriz).
- Si el informe de revisión también se exporta a un archivo para compartirlo.
