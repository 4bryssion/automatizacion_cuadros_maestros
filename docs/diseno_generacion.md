# Generación del cuadro: progreso y cuadro generado

Boceto v1.0. Todas las imágenes están en [`mockups/`](../mockups/) y se regeneran con `tools/boceto_todos.py`.
Tras la alerta de confirmación ("Sí, generar cuadro maestro") se abren estos modales sobre la ventana desde la que se generó.

## Dónde se guarda el cuadro

- **Carpeta:** subcarpeta `Cuadros generados`, dentro de la carpeta de los Excel. Así los cuadros no se mezclan con los Excel fuente que lee el programa.
- **Nombre:** `Cuadro maestro - <Programa> - <vigencia> - <AAAA-MM-DD> <HHMM>.xlsx` (ejemplo: `Cuadro maestro - Fisioterapia - 2019-2023 - 2026-11-23 1432.xlsx`).
- **Siempre un archivo nuevo.** Generar de nuevo no sobrescribe ni borra el anterior.
- Aviso en la alerta de confirmación: "crea un archivo nuevo en la subcarpeta Cuadros generados".

## Progreso de generación (30)

- Cinco pasos: leer la Matriz, leer la Movilidad anual, leer Internacionalización en casa, cruzar, escribir el cuadro.
- Cada paso tiene estado: hecho (verde), hecho con aviso (naranja, por ejemplo "falta 2021"), en curso (anillo) o pendiente (gris).
- Barra de avance por pasos y tiempo transcurrido; sin porcentaje, para no prometer una precisión que no hay.
- Aviso: no abrir ni editar los Excel de la carpeta mientras se genera. Los originales no se modifican.
- **Cancelar generación** y la **X** hacen lo mismo y son inmediatos: no se crea ningún archivo. Los cambios pendientes siguen pendientes y la última generación guardada no cambia.
- El cuadro se escribe en un archivo temporal y se renombra al final, para que una cancelación o un fallo no dejen un archivo a medias.

## Cuadro generado (31, 32, 33)

| Caso | Se abre sobre | Botón principal | Secundario | Cierra |
|---|---|---|---|---|
| Primera vez, con avisos (31) | Ventana principal | Ver revisión (8) | Abrir cuadro | Cerrar |
| De nuevo, desde la revisión (32) | Revisión | Abrir cuadro | Volver a la revisión | — |
| Sin avisos (33) | Ventana principal | Abrir cuadro | Cerrar | — |

- Muestra nombre y carpeta del archivo (con **Abrir carpeta**), y las mismas cifras de la vista previa: archivos leídos, convenios en el cuadro, movilidades contadas y avisos.
- Los avisos se resumen por grupo (corrige el Excel / resuélvelo aquí / informativos), con las mismas cuentas que Ver revisión (2 / 4 / 2; después de recargar 1 / 4 / 2).
- Al generar de nuevo se indica que el cuadro anterior no se modificó y se muestran las diferencias (+1 convenio, +43 movilidades, 1 aviso menos).
- Al terminar queda guardada la **última generación** y **Ver revisión** se activa en la ventana principal (enlace verde subrayado; gris cuando todavía no hay generación).

## Imágenes

| Archivo | Qué muestra |
|---|---|
| `30_modal_progreso_generacion.png` | Progreso con el paso 3 en curso |
| `31_modal_cuadro_generado.png` | Primera generación con 8 avisos |
| `32_modal_cuadro_generado_de_nuevo.png` | Generación desde la revisión, con 7 avisos |
| `33_modal_cuadro_generado_sin_avisos.png` | Generación sin avisos |
