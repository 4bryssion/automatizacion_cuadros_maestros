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
| Resuélvelo aquí en el programa | Naranja | Dentro del programa, sin tocar el Excel | Institución sin coincidencia; columna sin identificar; programa nuevo en la matriz que no está en la lista de Configuración (botón **Abrir Programas**) |
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

## Salir sin generar de nuevo: no se permite

Si al recargar **hubo cambios** y la persona intenta salir sin generar el cuadro de nuevo, el programa la obliga a generarlo.

- **Qué cuenta como "hubo cambios":** que el cuadro que saldría ahora sea distinto del último generado. Se compara el
  resultado, no los archivos: guardar un Excel sin cambiar nada no obliga a nada. **También cuentan los cambios de configuración
  hechos después de generar** (por ejemplo, una regla de cruce): el modal los lista ("Configuración cambiada desde que generaste: Reglas de cruce (1)").
- **Cuándo se activa:** al cerrar la ventana, al pulsar "Volver al cuadro maestro" o al cambiar la carpeta, el programa o la vigencia mientras hay cambios sin incluir (en ese caso el aviso ofrece **Generar cuadro de nuevo** y **Cancelar el cambio**; ver [diseno_apertura.md](diseno_apertura.md)).
- **Qué aparece:** un modal con el resumen (avisos resueltos, avisos nuevos, configuración cambiada, filas del cuadro que cambian) y dos opciones:
  **Generar cuadro de nuevo** (principal) y **Volver a la revisión**. No hay "Salir sin generar". La X del modal equivale a *Volver*.
- **Si el programa se cierra de otra forma** (corte de luz, administrador de tareas): el estado "cambios sin incluir" queda guardado
  y el modal aparece al abrir el programa la próxima vez.
- **Si la generación falla** (por ejemplo, el archivo de salida está abierto): el programa explica la causa y deja salir; el estado
  pendiente se conserva para la próxima apertura.
- Imagen: `revision_salir.png`.

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

- Aparece una franja con el resultado: "Antes 8 avisos, ahora 7" y tres contadores: **resueltos**, **siguen**, **nuevo**.
- Los avisos resueltos se agrupan arriba, en una caja verde, con lo que se logró.
- Cada aviso que sigue lleva una marca: **Sigue pendiente** (naranja), **Sin cambios** (gris) o **Nuevo** (magenta).
  Un aviso nuevo puede aparecer por una corrección: en el ejemplo, la fecha que se escribió quedó posterior a la de fin.
- La barra inferior explica que el cuadro anterior no cambió y que hay que generar de nuevo.

## Última generación guardada

Para que **Ver revisión** y el modal de arriba funcionen al volver a abrir el programa, se guarda la **última generación**: programa, vigencia,
carpeta, hora, avisos y si hay cambios sin incluir. Por eso Ver revisión sigue activo al reabrir (solo está desactivado si nunca se ha generado)
y el programa sabe qué mostrar. No contiene datos de personas.

## Confirmar varias sugerencias a la vez

El encabezado del grupo "Resuélvelo aquí" lleva el botón **Confirmar sugerencias (3)**, que abre el modal de confirmación en bloque
(ver [diseno_elegir_y_confirmar.md](diseno_elegir_y_confirmar.md)). Cada aviso conserva además su propio botón.

## Cómo se llega a Configuración desde la revisión

Los botones de los avisos (**Abrir Fuentes de datos**, **Elegir institución…**, **Abrir Programas**) abren el modal correspondiente **encima de la revisión**; no
llevan a la pantalla de Configuración. Al cerrarlo se vuelve a la revisión y se pulsa **Recargar archivos**. Lo mismo vale para los avisos de la
vista previa (ver [diseno_previsualizar_y_pruebas.md](diseno_previsualizar_y_pruebas.md)).

## Imágenes

| Archivo | Qué muestra |
|---|---|
| `revision_antes_arriba.png` | Primera vista, con los avisos que se corrigen en el Excel |
| `revision_antes_abajo.png` | Final de la lista: avisos del programa e informativos |
| `revision_despues.png` | Estado después de recargar: resueltos, pendientes y nuevo |
| `revision_salir.png` | Modal que obliga a generar de nuevo al salir con cambios sin incluir |

## Por definir

- Texto exacto de cada aviso para los casos que aparezcan con datos reales.
- Si el informe de revisión también se exporta a un archivo para compartirlo.
