# Campos del cuadro maestro y Fuentes de datos

Boceto v0.7. Imágenes generadas con `tools/boceto_campos_fuentes.py`: `modal_campos.png`, `modal_fuentes.png` y `configuracion.png` (actualizada).

## Campos del cuadro maestro

Define las columnas del Excel que se genera. Es una lista ordenable, con un editor que se abre dentro de la fila.

| Elemento | Comportamiento |
|---|---|
| Orden | Se arrastra con el agarre de seis puntos; el número de la fila cambia. |
| Nombre en el cuadro | Texto libre. Lo que se escribe es el encabezado del cuadro. |
| De dónde sale el dato | Etiqueta de color + detalle: **Matriz** (verde), **Reportes** (naranja), **Calculado** (gris) o **Vacío** (contorno). |
| Tipo | Número, Texto, Texto calculado u Opciones. |
| Acciones | Lápiz (abre el editor) y papelera. Los campos base muestran un candado en lugar de la papelera. |
| Crear campo | Botón verde arriba a la derecha; abre el mismo editor en blanco. |

**Editor de un campo:** nombre en el cuadro, tipo de dato, fuente del dato (qué Excel), columna del Excel y estado de la
coincidencia (Exacta, Por confirmar, Sin identificar). Cancelar y Guardar; Enter guarda y Esc cancela.

**Campos base:** Institución, Resultados concretos, Vigencia (años) y Activo. El programa los necesita para calcular, así que se
pueden renombrar pero no eliminar (tooltip: "Campo base: no se puede eliminar"). Los demás se quitan, se crean o se reordenan.

Los campos de ejemplo salen del cuadro real: No., Institución, Breve objeto, Resultados concretos, Vigencia (años), Activo,
Nº de usuarios y No aplica (estos dos últimos quedan vacíos).

## Fuentes de datos

Define cómo reconoce el programa cada tipo de Excel. Dos paneles: a la izquierda las fuentes, a la derecha el detalle de la elegida.

**Lista de fuentes:** Matriz de convenios, Movilidad e Internacionalización en casa. Cada una muestra su semáforo:
exactas (verde), por confirmar (naranja) y sin identificar (magenta). **Agregar fuente** crea otra.

**Detalle de una fuente:**

1. **Cómo se encuentra el archivo:** texto que contiene el nombre del archivo y cómo se leen el año y el semestre.
2. **Fila de encabezados:** detección automática (activada por defecto) y la fila detectada en cada archivo.
3. **Qué columna trae cada dato:** tabla *dato que necesita → columna del Excel → estado*. Si una columna no se identifica, la fila
   se marca en rosa con **Elegir columna…**, y lo elegido queda guardado para los próximos archivos.
4. **Qué filas se usan:** casillas con los filtros (solo el programa elegido; omitir actividades sin institución, que se cuentan aparte).

Abajo: **Probar con un archivo…** y **Listo**. Los cambios se guardan al instante.

## Coherencia con otras pantallas

- El aviso "Columna sin identificar: «Vínculo»" de [Ver revisión](diseno_revision.md) abre esta pantalla y muestra la misma fila
  (*Tipo de persona*, sin identificar).
- La tarjeta **Fuentes de datos** de Configuración ahora muestra tres puntos: 20 exactas, 1 por confirmar y 1 sin identificar
  (antes eran dos colores).
