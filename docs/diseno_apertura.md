# Primera apertura y reapertura

Boceto v0.13. Imágenes generadas con `tools/boceto_apertura.py` (`python3 -I tools/boceto_apertura.py <carpeta_marca> <salida>`).

## Primera apertura (34)

- La ventana principal sale vacía: carpeta, programa y vigencia con texto de ayuda en gris ("Elige la carpeta donde están tus Excel", "Elige un programa", "Año").
- Mensaje de bienvenida: el programa ya trae la configuración inicial (25 programas de Pereira), se ajusta en Configuración y los ajustes se guardan solos.
- El campo de la carpeta lleva el borde verde grueso (primer paso).
- **Generar cuadro maestro** y **Previsualizar cuadro** están desactivados, con la nota "Se activan al completar los pasos 1, 2 y 3". **Ver revisión** está desactivado hasta que haya una generación guardada. **Configuración** siempre está disponible.
- En lugar de la tabla de archivos: "Todavía no hay carpeta elegida".
- Al abrir por primera vez se crea la configuración inicial y se guarda en los dos lugares (ver [decisiones_de_proyecto.md](decisiones_de_proyecto.md)).

## Reapertura (35, 36, 37)

Al abrir de nuevo, el programa recuerda carpeta, programa y vigencia, y muestra la **última generación guardada**.

| Estado | Qué se ve |
|---|---|
| Al día (35) | Franja gris "Último cuadro: programa · vigencia · cuándo · N avisos" con **Abrir cuadro** y **Abrir carpeta**. **Ver revisión** activo. |
| Cambios sin incluir (36) | Al abrir aparece el aviso "Quedaron cambios sin incluir": resumen (avisos resueltos y nuevos, configuración cambiada, filas que cambian) y los botones **Generar cuadro de nuevo** (principal) y **Ver revisión**. |
| Tras cerrar ese aviso (37) | La franja se pone naranja: "tiene cambios sin incluir. Genera de nuevo para incluirlos". |

- Causas de "cambios sin incluir" al reabrir: cierre inesperado (corte de luz, administrador de tareas) o generación fallida; el estado se guardó antes de cerrar.
- Se puede seguir en la ventana principal con cambios pendientes; lo que no se permite es **salir** o **cambiar de programa** sin generar de nuevo (regla de [diseno_revision.md](diseno_revision.md)).
- Solo se guarda **la última generación**, no una por programa. La franja y **Ver revisión** siempre se refieren a ella y nombran su programa, aunque en la ventana esté elegido otro.
- Si alguien edita un Excel con el programa cerrado, **no se detecta**: el estado pendiente solo guarda lo que se sabía al cerrar. **Previsualizar cuadro** o **Recargar archivos** lo muestran.

## Qué se actualiza al cambiar carpeta, programa o vigencia

- La tabla **Archivos que se usarán** (y su marca "N de M encontrados" y el aviso naranja) depende de la **carpeta** y de la **vigencia** (y de lo definido en Configuración › Fuentes de datos), no del programa: los Excel traen todos los programas y el programa elegido solo filtra filas dentro de ellos.
- Se vuelve a leer al cambiar la carpeta o la vigencia, al pulsar **Actualizar** y al volver a la ventana.
- La última generación (franja y Ver revisión) **no cambia** hasta que se genere de nuevo.

## Cambiar carpeta, programa o vigencia con cambios sin incluir (38)

- Con cambios sin incluir, cambiar cualquiera de los tres campos abre un aviso: "Antes de cambiar de programa" (o "…de carpeta", "…de vigencia"), con el resumen de lo que falta incluir.
- **Generar cuadro de nuevo** (principal): genera y, al terminar, aplica el cambio pedido y vuelve a leer la tabla de archivos.
- **Cancelar el cambio** (y la X): el campo queda como estaba.
- Sin cambios sin incluir, los tres campos se cambian libremente.

## Imágenes

| Archivo | Qué muestra |
|---|---|
| `34_primera_apertura.png` | Primera apertura con bienvenida y controles desactivados |
| `35_reapertura_al_dia.png` | Reapertura con la franja "Último cuadro" |
| `36_reapertura_aviso_cambios_sin_incluir.png` | Aviso al abrir con cambios sin incluir |
| `37_reapertura_cambios_sin_incluir_tras_cerrar_aviso.png` | Ventana principal con la franja naranja |
| `38_cambiar_programa_con_cambios_sin_incluir.png` | Aviso al cambiar programa, carpeta o vigencia con cambios sin incluir |
